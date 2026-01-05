import pytest
import os

def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "DXF Generator API is running"}

def test_generate_ibeam_endpoint(client):
    """Test the single I-Beam generation endpoint."""
    payload = {
        "total_depth": 300,
        "flange_width": 150,
        "web_thickness": 8,
        "flange_thickness": 12
    }
    response = client.post("/api/v1/ibeam", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/dxf"
    # Filename should be in the headers
    assert "ibeam_300x150.dxf" in response.headers["content-disposition"]

def test_generate_ibeam_invalid_payload(client):
    """Test I-Beam generation with invalid payload."""
    payload = {
        "total_depth": 10,  # Too small
        "flange_width": 150,
        "web_thickness": 8,
        "flange_thickness": 12
    }
    response = client.post("/api/v1/ibeam", json=payload)
    assert response.status_code == 400
    assert "detail" in response.json()

def test_generate_ibeam_batch_endpoint(client):
    """Test the batch I-Beam generation endpoint."""
    payload = {
        "items": [
            {"total_depth": 300, "flange_width": 150, "web_thickness": 8, "flange_thickness": 12},
            {"total_depth": 400, "flange_width": 200, "web_thickness": 10, "flange_thickness": 15}
        ]
    }
    # Fix expected path
    response = client.post("/api/v1/ibeam/batch", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert "ibeams_batch.zip" in response.headers["content-disposition"]

def test_generate_column_endpoint(client):
    """Test the single Column generation endpoint."""
    payload = {"width": 200, "height": 200}
    response = client.post("/api/v1/column", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/dxf"
    assert "column_200x200.dxf" in response.headers["content-disposition"]

def test_generate_column_batch_endpoint(client):
    """Test the batch Column generation endpoint."""
    payload = {
        "items": [
            {"width": 200, "height": 200},
            {"width": 300, "height": 300}
        ]
    }
    response = client.post("/api/v1/column/batch", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert "columns_batch.zip" in response.headers["content-disposition"]

def test_generate_ibeam_batch_exceed_limit(client):
    """Test I-Beam batch generation fails when exceeding system limit."""
    # Create 51 items (limit is 50)
    items = [{"total_depth": 300, "flange_width": 150, "web_thickness": 8, "flange_thickness": 12}] * 51
    response = client.post("/api/v1/ibeam/batch", json={"items": items})
    assert response.status_code == 400
    assert "Batch size exceeds maximum limit" in response.json()["detail"]

def test_generate_column_batch_exceed_limit(client):
    """Test Column batch generation fails when exceeding system limit."""
    # Create 51 items (limit is 50)
    items = [{"width": 200, "height": 200}] * 51
    response = client.post("/api/v1/column/batch", json={"items": items})
    assert response.status_code == 400
    assert "Batch size exceeds maximum limit" in response.json()["detail"]
