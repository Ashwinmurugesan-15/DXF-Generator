import pytest
from dxf_generator.domain.column import Column
from dxf_generator.exceptions.geometry import ColumnGeometryError

def test_column_creation_success():
    """Test successful creation of a Column."""
    column = Column(width=200, height=200)
    assert column.data["width"] == 200
    assert column.data["height"] == 200

def test_column_creation_failure_negative_values():
    """Test Column creation failure with negative values."""
    with pytest.raises(ColumnGeometryError):
        Column(width=-200, height=200)

def test_column_creation_failure_zero_values():
    """Test Column creation failure with zero values."""
    with pytest.raises(ColumnGeometryError):
        Column(width=0, height=200)
