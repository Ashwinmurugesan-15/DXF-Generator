import pytest
from unittest.mock import MagicMock, patch, mock_open
from dxf_generator.services.dxf_service import DXFService

class MockComponent:
    def __init__(self, data):
        self.data = data
    
    def generate_dxf(self, filename):
        pass

@pytest.fixture
def dxf_service():
    # Reset caches before each test using new API
    DXFService.clear_caches()
    return DXFService

def test_get_cache_key():
    comp = MockComponent({"a": 1})
    key1 = DXFService.get_cache_key(comp)
    key2 = DXFService.get_cache_key(comp)
    assert key1 == key2
    assert "MockComponent" in key1


@patch("dxf_generator.services.dxf_service.DXFGenerator.generate")
def test_save_delegates_to_generator(mock_generate, dxf_service):
    component = MockComponent({"x": 1})
    mock_generate.return_value = b"content"

    result = dxf_service.save(component, "out.dxf")

    assert result == "out.dxf"
    mock_generate.assert_called_once_with(component, "out.dxf")

@patch("dxf_generator.services.dxf_generator.open", new_callable=mock_open, read_data=b"generated_content")
def test_save_cached_miss_then_hit(mock_file, dxf_service):
    component = MockComponent({"test": "data"})
    filename = "test.dxf"
    
    # First call - Cache Miss
    with patch.object(component, 'generate_dxf') as mock_gen:
        content = dxf_service.save_cached(component, filename)
        
        assert content == b"generated_content"
        mock_gen.assert_called_once_with(filename)
        assert dxf_service._generation_cache.size == 1
    
    # Second call - Cache Hit
    with patch.object(component, 'generate_dxf') as mock_gen:
        content_hit = dxf_service.save_cached(component, filename)
        
        assert content_hit == b"generated_content"
        mock_gen.assert_not_called() # Should use cache

def test_cache_eviction(dxf_service):
    """Test that cache eviction works when limit exceeded."""
    # Fill cache to limit (500)
    for i in range(505):
        key = f"key_{i}"
        dxf_service._generation_cache.set(key, b"value")
    
    # Should not exceed max size
    assert dxf_service._generation_cache.size <= 500


def test_clear_caches(dxf_service):
    dxf_service._generation_cache.set("k1", b"v1")
    dxf_service._parse_cache.set("k2", {"type": "column", "data": {}})

    dxf_service.clear_caches()

    assert dxf_service._generation_cache.size == 0
    assert dxf_service._parse_cache.size == 0


def test_get_cache_stats(dxf_service):
    stats = dxf_service.get_cache_stats()
    assert "generation" in stats
    assert "parse" in stats
    assert set(stats["generation"].keys()) == {"hits", "misses", "size", "hit_rate"}
    assert set(stats["parse"].keys()) == {"hits", "misses", "size", "hit_rate"}

@patch("dxf_generator.services.dxf_generator.open", new_callable=mock_open, read_data=b"batch_data")
def test_save_batch(mock_file, dxf_service):
    """
    Test that save_batch submits tasks and returns immediately (non-blocking).
    """
    components = [MockComponent({"id": i}) for i in range(10)]
    filenames = [f"file_{i}.dxf" for i in range(10)]
    
    import time
    start = time.time()
    generated = dxf_service.save_batch(components, filenames)
    elapsed = time.time() - start
    
    # Method should return immediately
    assert elapsed < 0.5, f"save_batch blocked for {elapsed}s, should return immediately"
    
    # Returns only cache hits (none for new items)
    assert generated == [], "New items should be submitted async, not returned"


@patch("dxf_generator.services.dxf_service.DXFGenerator.write_content")
def test_save_batch_writes_cache_hits(mock_write_content, dxf_service):
    components = [MockComponent({"id": 1}), MockComponent({"id": 2})]
    filenames = ["a.dxf", "b.dxf"]

    key0 = dxf_service.get_cache_key(components[0])
    dxf_service._generation_cache.set(key0, b"a")

    returned = dxf_service.save_batch(components, filenames)

    assert returned == ["a.dxf"]
    mock_write_content.assert_called_once_with(b"a", "a.dxf")

@patch("dxf_generator.services.dxf_parser.ezdxf")
def test_parse_cache_hit(mock_ezdxf, dxf_service):
    # Setup mock
    mock_polyline = MagicMock()
    mock_polyline.get_points.return_value = [
        (0, 0), (100, 0), (100, 10),  # 12 points for I-beam
        (60, 10), (60, 90), (100, 90),
        (100, 100), (0, 100), (0, 90),
        (-60, 90), (-60, 10), (0, 10)
    ]
    mock_msp = MagicMock()
    mock_msp.query.return_value = [mock_polyline]
    mock_doc = MagicMock()
    mock_doc.modelspace.return_value = mock_msp
    mock_ezdxf.readfile.return_value = mock_doc
    
    # Mock file hash
    with patch("dxf_generator.services.dxf_parser.DXFParser.get_file_hash", return_value="hash1"):
        # First call - cache miss
        result1 = dxf_service.parse("test.dxf")
        assert result1["type"] == "ibeam"
        
        # Second call - cache hit (ezdxf not called again)
        mock_ezdxf.readfile.reset_mock()
        result2 = dxf_service.parse("test.dxf")
        assert result2 == result1
        mock_ezdxf.readfile.assert_not_called()

@patch("dxf_generator.services.dxf_parser.ezdxf")
def test_parse_new_file(mock_ezdxf, dxf_service):
    # Setup mock for column (4 points)
    mock_polyline = MagicMock()
    mock_polyline.get_points.return_value = [
        (0, 0), (400, 0), (400, 300), (0, 300)
    ]
    mock_msp = MagicMock()
    mock_msp.query.return_value = [mock_polyline]
    mock_doc = MagicMock()
    mock_doc.modelspace.return_value = mock_msp
    mock_ezdxf.readfile.return_value = mock_doc
    
    with patch("dxf_generator.services.dxf_parser.DXFParser.get_file_hash", return_value="hash_col"):
        result = dxf_service.parse("column.dxf")
        
        assert result["type"] == "column"
        assert result["data"]["width"] == 400
        assert result["data"]["height"] == 300
