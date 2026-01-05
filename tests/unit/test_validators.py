import pytest
from dxf_generator.validators.ibeam_validator import IBeamValidator
from dxf_generator.validators.column_validator import ColumnValidator
from dxf_generator.exceptions.schema import IBeamSchemaError, ColumnSchemaError
from dxf_generator.exceptions.geometry import IBeamGeometryError, ColumnGeometryError

def test_ibeam_validator_schema():
    """Test I-Beam schema validation."""
    with pytest.raises(IBeamSchemaError):
        IBeamValidator.validate({"total_depth": 300})  # Missing fields

def test_ibeam_validator_geometry():
    """Test I-Beam geometry validation."""
    valid_data = {
        "length": 1000,
        "total_depth": 300,
        "flange_width": 150,
        "web_thickness": 8,
        "flange_thickness": 12
    }
    # Should not raise
    IBeamValidator.validate(valid_data)
    
    invalid_data = valid_data.copy()
    invalid_data["total_depth"] = 10  # Too small
    with pytest.raises(IBeamGeometryError):
        IBeamValidator.validate(invalid_data)

def test_column_validator_schema():
    """Test Column schema validation."""
    with pytest.raises(ColumnSchemaError):
        ColumnValidator.validate({"width": 200})  # Missing height

def test_column_validator_geometry():
    """Test Column geometry validation."""
    valid_data = {"width": 200, "height": 200}
    # Should not raise
    ColumnValidator.validate(valid_data)
    
    invalid_data = {"width": 0, "height": 200}
    with pytest.raises(ColumnGeometryError):
        ColumnValidator.validate(invalid_data)
