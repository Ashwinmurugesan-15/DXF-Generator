"""
Unit tests for DXFParser component.
Tests DXF file parsing, shape identification, and dimension extraction.
"""
import pytest
from unittest.mock import MagicMock, patch, mock_open
import ezdxf
from dxf_generator.services.dxf_parser import DXFParser


@pytest.fixture
def mock_ibeam_polyline():
    """Create a mock polyline with I-Beam vertices (12 points)."""
    polyline = MagicMock()
    # I-Beam: b=100 (flange_width), tf=10 (flange_thickness), h=200 (depth), tw=8 (web)
    # p[4][0] = (b + tw) / 2 = (100 + 8) / 2 = 54
    points = [(0, 0)] * 12
    points[1] = (100, 0)   # b = flange_width
    points[2] = (100, 10)  # tf = flange_thickness
    points[4] = (54, 10)   # For tw calculation
    points[6] = (100, 200) # h = total_depth
    polyline.get_points.return_value = points
    return polyline


@pytest.fixture
def mock_column_polyline():
    """Create a mock polyline with Column vertices (4 points)."""
    polyline = MagicMock()
    points = [(0, 0), (300, 0), (300, 400), (0, 400)]
    polyline.get_points.return_value = points
    return polyline


def test_get_file_hash():
    """Test file hash generation."""
    mocked_open = mock_open()
    mocked_open.return_value.read.side_effect = [b"chunk", b""]
    with patch("builtins.open", mocked_open):
        with patch("dxf_generator.services.dxf_parser.hashlib") as mock_hashlib:
            mock_hasher = MagicMock()
            mock_hasher.hexdigest.return_value = "abc123def456"
            mock_hashlib.md5.return_value = mock_hasher
            
            result = DXFParser.get_file_hash("test.dxf")
            
            assert result == "abc123def456"


@patch("dxf_generator.services.dxf_parser.ezdxf")
def test_parse_ibeam(mock_ezdxf, mock_ibeam_polyline):
    """Test parsing I-Beam from DXF file."""
    mock_ezdxf.DXFError = ezdxf.DXFError
    mock_msp = MagicMock()
    mock_msp.query.return_value = [mock_ibeam_polyline]
    mock_doc = MagicMock()
    mock_doc.modelspace.return_value = mock_msp
    mock_ezdxf.readfile.return_value = mock_doc
    
    result = DXFParser.parse("ibeam.dxf")
    
    assert result["type"] == "ibeam"
    assert result["data"]["flange_width"] == 100.0
    assert result["data"]["total_depth"] == 200.0
    assert result["data"]["flange_thickness"] == 10.0


@patch("dxf_generator.services.dxf_parser.ezdxf")
def test_parse_column(mock_ezdxf, mock_column_polyline):
    """Test parsing Column from DXF file."""
    mock_ezdxf.DXFError = ezdxf.DXFError
    mock_msp = MagicMock()
    mock_msp.query.return_value = [mock_column_polyline]
    mock_doc = MagicMock()
    mock_doc.modelspace.return_value = mock_msp
    mock_ezdxf.readfile.return_value = mock_doc
    
    result = DXFParser.parse("column.dxf")
    
    assert result["type"] == "column"
    assert result["data"]["width"] == 300.0
    assert result["data"]["height"] == 400.0


@patch("dxf_generator.services.dxf_parser.ezdxf")
def test_parse_no_polylines_raises_error(mock_ezdxf):
    """Test parsing file with no polylines raises ValueError."""
    mock_ezdxf.DXFError = ezdxf.DXFError
    mock_msp = MagicMock()
    mock_msp.query.return_value = []  # No polylines
    mock_doc = MagicMock()
    mock_doc.modelspace.return_value = mock_msp
    mock_ezdxf.readfile.return_value = mock_doc
    
    with pytest.raises(ValueError, match="No LWPOLYLINE found"):
        DXFParser.parse("empty.dxf")


@patch("dxf_generator.services.dxf_parser.ezdxf")
def test_parse_invalid_vertices_raises_error(mock_ezdxf):
    """Test parsing file with invalid vertex count raises ValueError."""
    mock_ezdxf.DXFError = ezdxf.DXFError
    mock_polyline = MagicMock()
    mock_polyline.get_points.return_value = [(0, 0)] * 7  # Invalid count
    mock_msp = MagicMock()
    mock_msp.query.return_value = [mock_polyline]
    mock_doc = MagicMock()
    mock_doc.modelspace.return_value = mock_msp
    mock_ezdxf.readfile.return_value = mock_doc
    
    with pytest.raises(ValueError, match="Unexpected number of vertices"):
        DXFParser.parse("invalid.dxf")


@patch("dxf_generator.services.dxf_parser.ezdxf")
def test_parse_dxf_error(mock_ezdxf):
    """Test DXFError is propagated correctly."""
    mock_ezdxf.DXFError = ezdxf.DXFError
    mock_ezdxf.readfile.side_effect = ezdxf.DXFError("Corrupt file")
    
    with pytest.raises(ezdxf.DXFError, match="Corrupt file"):
        DXFParser.parse("corrupt.dxf")


@patch("dxf_generator.services.dxf_parser.ezdxf")
def test_parse_generic_error_wrapped_as_valueerror(mock_ezdxf):
    """Test generic errors are wrapped as ValueError."""
    mock_ezdxf.DXFError = ezdxf.DXFError
    mock_ezdxf.readfile.side_effect = IOError("Disk error")
    
    with pytest.raises(ValueError, match="Failed to parse DXF"):
        DXFParser.parse("file.dxf")


def test_identify_shape_ibeam_12_points():
    """Test I-Beam identification with 12 points."""
    points = [(0, 0)] * 12
    points[1] = (150, 0)
    points[2] = (150, 15)
    points[4] = (79, 15)  # (150 + 8) / 2 = 79
    points[6] = (150, 300)
    
    result = DXFParser._identify_shape(points, "test.dxf")
    
    assert result["type"] == "ibeam"
    assert result["data"]["flange_width"] == 150.0
    assert result["data"]["total_depth"] == 300.0


def test_identify_shape_ibeam_13_points():
    """Test I-Beam identification with 13 points (closed polyline)."""
    points = [(0, 0)] * 13
    points[1] = (200, 0)
    points[2] = (200, 20)
    points[4] = (104, 20)
    points[6] = (200, 400)
    
    result = DXFParser._identify_shape(points, "test.dxf")
    
    assert result["type"] == "ibeam"


def test_identify_shape_column_4_points():
    """Test Column identification with 4 points."""
    points = [(0, 0), (250, 0), (250, 350), (0, 350)]
    
    result = DXFParser._identify_shape(points, "test.dxf")
    
    assert result["type"] == "column"
    assert result["data"]["width"] == 250.0
    assert result["data"]["height"] == 350.0


def test_identify_shape_column_5_points():
    """Test Column identification with 5 points (closed polyline)."""
    points = [(0, 0), (500, 0), (500, 600), (0, 600), (0, 0)]
    
    result = DXFParser._identify_shape(points, "test.dxf")
    
    assert result["type"] == "column"
    assert result["data"]["width"] == 500.0
    assert result["data"]["height"] == 600.0
