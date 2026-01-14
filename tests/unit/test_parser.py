import pytest
import ezdxf
from unittest.mock import MagicMock, patch
from dxf_generator.services.dxf_service import DXFService

@pytest.fixture
def dxf_service():
    DXFService.clear_caches()
    return DXFService

@patch("dxf_generator.services.dxf_parser.ezdxf")
@patch("dxf_generator.services.dxf_parser.DXFParser.get_file_hash", return_value="hash_parser")
def test_parse_success_ibeam(mock_hash, mock_ezdxf, dxf_service):
    mock_doc = MagicMock()
    mock_msp = MagicMock()
    mock_polyline = MagicMock()
    
    mock_ezdxf.readfile.return_value = mock_doc
    mock_doc.modelspace.return_value = mock_msp
    mock_msp.query.return_value = [mock_polyline]
    
    p = [(0,0)] * 13
    p[1] = (100, 0)
    p[2] = (100, 10)
    p[4] = (54, 10)
    p[6] = (100, 200)
    mock_polyline.get_points.return_value = p
    
    result = dxf_service.parse("test.dxf")
    
    assert result["type"] == "ibeam"
    assert result["data"]["flange_width"] == 100.0
    assert result["data"]["total_depth"] == 200.0

@patch("dxf_generator.services.dxf_parser.ezdxf")
@patch("dxf_generator.services.dxf_parser.DXFParser.get_file_hash", return_value="hash_parser_col")
def test_parse_success_column(mock_hash, mock_ezdxf, dxf_service):
    mock_doc = MagicMock()
    mock_msp = MagicMock()
    mock_polyline = MagicMock()
    
    mock_ezdxf.readfile.return_value = mock_doc
    mock_doc.modelspace.return_value = mock_msp
    mock_msp.query.return_value = [mock_polyline]
    
    p = [(0,0)] * 5
    p[1] = (300, 0)
    p[2] = (300, 400)
    mock_polyline.get_points.return_value = p
    
    result = dxf_service.parse("column.dxf")
    
    assert result["type"] == "column"
    assert result["data"]["width"] == 300.0
    assert result["data"]["height"] == 400.0

@patch("dxf_generator.services.dxf_parser.ezdxf")
@patch("dxf_generator.services.dxf_parser.DXFParser.get_file_hash", return_value="hash_fail")
def test_parse_no_polylines(mock_hash, mock_ezdxf, dxf_service):
    mock_ezdxf.DXFError = ezdxf.DXFError  # Use real exception class
    mock_doc = MagicMock()
    mock_msp = MagicMock()
    mock_ezdxf.readfile.return_value = mock_doc
    mock_doc.modelspace.return_value = mock_msp
    mock_msp.query.return_value = []
    
    with pytest.raises(ValueError, match="No LWPOLYLINE found"):
        dxf_service.parse("empty.dxf")

@patch("dxf_generator.services.dxf_parser.ezdxf")
@patch("dxf_generator.services.dxf_parser.DXFParser.get_file_hash", return_value="hash_fail_verts")
def test_parse_invalid_vertices(mock_hash, mock_ezdxf, dxf_service):
    mock_ezdxf.DXFError = ezdxf.DXFError  # Use real exception class
    mock_doc = MagicMock()
    mock_msp = MagicMock()
    mock_polyline = MagicMock()
    
    mock_ezdxf.readfile.return_value = mock_doc
    mock_doc.modelspace.return_value = mock_msp
    mock_msp.query.return_value = [mock_polyline]
    mock_polyline.get_points.return_value = [(0,0)] * 8
    
    with pytest.raises(ValueError, match="Unexpected number of vertices"):
        dxf_service.parse("invalid.dxf")
