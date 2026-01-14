import pytest
from unittest.mock import MagicMock, patch
from dxf_generator.drawing.drawing import DXFDrawing

@pytest.fixture
def dxf_drawing():
    with patch("dxf_generator.drawing.drawing.ezdxf.new"):
        drawing = DXFDrawing()
        drawing.msp = MagicMock() # Mock modelspace
        yield drawing

def test_draw_ibeam(dxf_drawing):
    data = {
        "total_depth": 200,
        "flange_width": 100,
        "web_thickness": 8,
        "flange_thickness": 10
    }
    
    dxf_drawing.draw_ibeam(data)
    
    # Verify add_lwpolyline was called
    dxf_drawing.msp.add_lwpolyline.assert_called_once()
    
    # Verify points (basic check of count and structure)
    call_args = dxf_drawing.msp.add_lwpolyline.call_args
    points = call_args[0][0]
    assert len(points) == 13 # 12 points + close
    assert points[0] == (0, 0)
    assert points[1] == (100, 0)

def test_draw_column(dxf_drawing):
    data = {
        "width": 300,
        "height": 400
    }
    
    dxf_drawing.draw_column(data)
    
    dxf_drawing.msp.add_lwpolyline.assert_called_once()
    
    call_args = dxf_drawing.msp.add_lwpolyline.call_args
    points = call_args[0][0]
    assert len(points) == 5 # 4 points + close
    assert points[2] == (300, 400)

@patch("dxf_generator.drawing.drawing.ezdxf.new")
def test_save(mock_new, dxf_drawing):
    # Setup mock doc
    mock_doc = MagicMock()
    dxf_drawing.doc = mock_doc
    
    dxf_drawing.save("output.dxf")
    
    mock_doc.saveas.assert_called_once_with("output.dxf")
