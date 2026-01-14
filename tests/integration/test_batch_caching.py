import pytest
from dxf_generator.services.dxf_service import DXFService

@pytest.fixture(autouse=True)
def clear_caches():
    DXFService.clear_caches()
    yield
    DXFService.clear_caches()

def test_ibeam_batch_caching(client):
    payload = {
        "items": [
            {"total_depth": 300, "flange_width": 150, "web_thickness": 10, "flange_thickness": 15},
            {"total_depth": 400, "flange_width": 200, "web_thickness": 12, "flange_thickness": 20}
        ]
    }
    
    # 1. First Request - Cache Miss
    # Note: Using prefix /api/v1/ based on main.py/conftest mounting
    response1 = client.post("/api/v1/ibeam/batch", json=payload)
    assert response1.status_code == 200, f"Request failed: {response1.text}"
    assert response1.headers["X-Cache"] == "MISS"
    content1 = response1.content
    
    # 2. Second Request (Identical) - Cache Hit
    response2 = client.post("/api/v1/ibeam/batch", json=payload)
    assert response2.status_code == 200
    assert response2.headers["X-Cache"] == "HIT"
    assert response2.content == content1
    
    # 3. Third Request (Different) - Cache Miss
    payload_diff = {
        "items": [
            {"total_depth": 300, "flange_width": 150, "web_thickness": 10, "flange_thickness": 15},
            # Changed item
            {"total_depth": 500, "flange_width": 200, "web_thickness": 12, "flange_thickness": 20}
        ]
    }
    response3 = client.post("/api/v1/ibeam/batch", json=payload_diff)
    assert response3.status_code == 200
    assert response3.headers["X-Cache"] == "MISS"
    assert response3.content != content1

def test_column_batch_caching(client):
    payload = {
        "items": [
            {"width": 300, "height": 300},
            {"width": 400, "height": 400}
        ]
    }
    
    # 1. First Request - Cache Miss
    response1 = client.post("/api/v1/column/batch", json=payload)
    assert response1.status_code == 200
    assert response1.headers["X-Cache"] == "MISS"
    content1 = response1.content
    
    # 2. Second Request (Identical) - Cache Hit
    response2 = client.post("/api/v1/column/batch", json=payload)
    assert response2.status_code == 200
    assert response2.headers["X-Cache"] == "HIT"
    assert response2.content == content1

def test_batch_cache_order_independence(client):
    """Test that batch caching is order-independent (sorted keys)."""
    item1 = {"width": 300, "height": 300}
    item2 = {"width": 400, "height": 400}
    
    payload1 = {"items": [item1, item2]}
    payload2 = {"items": [item2, item1]} # Same items, different order
    
    # 1. Request 1
    response1 = client.post("/api/v1/column/batch", json=payload1)
    assert response1.status_code == 200
    assert response1.headers["X-Cache"] == "MISS"
    
    # 2. Request 2 (Different order)
    # Since we implemented sorted keys in DXFService.get_batch_key, this should be a HIT
    response2 = client.post("/api/v1/column/batch", json=payload2)
    assert response2.status_code == 200
    
    assert response2.headers["X-Cache"] == "HIT", "Batch cache should be order-independent"
