"""
Unit tests for DXFGenerator component.
Tests DXF file generation and content writing.
"""
import pytest
from unittest.mock import patch, mock_open
from dxf_generator.services.dxf_generator import DXFGenerator


class MockComponent:
    """Mock component for testing generation."""
    def __init__(self, data):
        self.data = data
        self.generate_called = False
        self.generated_filename = None
    
    def generate_dxf(self, filename):
        self.generate_called = True
        self.generated_filename = filename


@pytest.fixture
def mock_file_content():
    return b"DXF file content bytes"


def test_generate_calls_component_generate_dxf(mock_file_content):
    """Test generate calls component's generate_dxf method."""
    component = MockComponent({"width": 100})
    
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        DXFGenerator.generate(component, "output.dxf")
    
    assert component.generate_called is True
    assert component.generated_filename == "output.dxf"


def test_generate_returns_file_content(mock_file_content):
    """Test generate returns the generated file content."""
    component = MockComponent({"width": 100})
    
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        content = DXFGenerator.generate(component, "output.dxf")
    
    assert content == mock_file_content


def test_generate_reads_file_after_generation(mock_file_content):
    """Test generate reads file content after component generates it."""
    component = MockComponent({"test": "data"})
    
    mock_file = mock_open(read_data=mock_file_content)
    with patch("builtins.open", mock_file):
        DXFGenerator.generate(component, "test.dxf")
    
    # Verify file was opened for reading
    mock_file.assert_called_with("test.dxf", "rb")


def test_write_content_writes_bytes():
    """Test write_content writes bytes to file."""
    content = b"DXF binary content"
    
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        DXFGenerator.write_content(content, "cached.dxf")
    
    # Verify file was opened for writing
    mock_file.assert_called_once_with("cached.dxf", "wb")
    mock_file().write.assert_called_once_with(content)


def test_generate_propagates_component_error():
    """Test generate propagates errors from component."""
    class FailingComponent:
        data = {}
        def generate_dxf(self, filename):
            raise RuntimeError("Generation failed")
    
    component = FailingComponent()
    
    with pytest.raises(RuntimeError, match="Generation failed"):
        DXFGenerator.generate(component, "fail.dxf")


def test_generate_with_different_data():
    """Test generate works with different component data."""
    data_sets = [
        {"type": "ibeam", "depth": 300},
        {"type": "column", "width": 200, "height": 200},
        {"complex": {"nested": "data"}}
    ]
    
    for data in data_sets:
        component = MockComponent(data)
        with patch("builtins.open", mock_open(read_data=b"content")):
            result = DXFGenerator.generate(component, "test.dxf")
        
        assert result == b"content"
        assert component.data == data
