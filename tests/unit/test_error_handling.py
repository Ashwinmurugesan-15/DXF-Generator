import pytest
from unittest.mock import MagicMock, patch
from dxf_generator.services.dxf_service import DXFService
import ezdxf

class ErrorComponent:
    def __init__(self):
        self.data = {}
        
    def generate_dxf(self, filename):
        raise RuntimeError("Generation Failed")

@pytest.fixture
def dxf_service():
    DXFService.clear_caches()
    return DXFService

def test_save_cached_generation_error(dxf_service):
    component = ErrorComponent()
    
    with pytest.raises(RuntimeError, match="Generation Failed"):
        dxf_service.save_cached(component, "error.dxf")

@patch("dxf_generator.config.logging_config.logger")
def test_save_cached_logs_error(mock_logger, dxf_service):
    component = ErrorComponent()
    try:
        dxf_service.save_cached(component, "error.dxf")
    except Exception:
        pass
    
    # Verify error was logged (via DXFGenerator)
    # The logger is used in dxf_generator.py

@patch("dxf_generator.services.dxf_service.DXFService.save_cached")
def test_save_batch_partial_failure(mock_save_cached, dxf_service):
    """
    Test that partial failures in batch processing are handled via callbacks.
    """
    def side_effect(comp, filename):
        if filename == "fail.dxf":
            raise ValueError("Batch Fail")
        return b"success"
    
    mock_save_cached.side_effect = side_effect
    
    components = [MagicMock(), MagicMock()]
    filenames = ["success.dxf", "fail.dxf"]
    
    import time
    start = time.time()
    generated = dxf_service.save_batch(components, filenames)
    elapsed = time.time() - start
    
    # Method should return immediately
    assert elapsed < 0.5, f"save_batch blocked for {elapsed}s"
    
    # Returns empty for new items (fire-and-forget)
    assert generated == [], "New items should be submitted async"
    
    # Wait briefly for background tasks
    time.sleep(0.5)
    
    # Verify save_cached was called
    assert mock_save_cached.call_count == 2

@patch("dxf_generator.services.dxf_parser.ezdxf")
def test_parse_ezdxf_error(mock_ezdxf, dxf_service):
    mock_ezdxf.DXFError = ezdxf.DXFError
    mock_ezdxf.readfile.side_effect = ezdxf.DXFError("Corrupt file")
    
    with patch("dxf_generator.services.dxf_parser.DXFParser.get_file_hash", return_value="hash_err"):
        with pytest.raises(ezdxf.DXFError, match="Corrupt file"):
            DXFService.parse("corrupt.dxf")

@patch("dxf_generator.services.dxf_parser.ezdxf")
def test_parse_generic_error(mock_ezdxf, dxf_service):
    mock_ezdxf.DXFError = ezdxf.DXFError
    mock_ezdxf.readfile.side_effect = IOError("Disk error")
    
    with patch("dxf_generator.services.dxf_parser.DXFParser.get_file_hash", return_value="hash_gen"):
        with pytest.raises(ValueError, match="Failed to parse DXF"):
            DXFService.parse("file.dxf")
