import pytest
from dxf_generator.validators.ibeam_validator import IBeamValidator
from dxf_generator.validators.column_validator import ColumnValidator
from dxf_generator.exceptions.schema import IBeamSchemaError, ColumnSchemaError
from dxf_generator.exceptions.geometry import IBeamGeometryError, ColumnGeometryError

def test_ibeam_validator_schema():
    """Test I-Beam schema validation."""
    with pytest.raises(IBeamSchemaError, match="Missing field: length"):
        IBeamValidator.validate({"total_depth": 300})
        
    with pytest.raises(IBeamSchemaError, match="length must be numeric"):
        IBeamValidator.validate({
            "length": "1000",
            "total_depth": 300,
            "flange_width": 150,
            "web_thickness": 8,
            "flange_thickness": 12
        })

def test_ibeam_validator_geometry_limits():
    """Test I-Beam geometry validation (absolute limits)."""
    base_data = {
        "length": 1000,
        "total_depth": 300,
        "flange_width": 150,
        "web_thickness": 8,
        "flange_thickness": 12
    }

    # Test negative values
    invalid_neg = base_data.copy()
    invalid_neg["length"] = -1
    with pytest.raises(IBeamGeometryError, match="length must be greater than 0"):
        IBeamValidator.validate(invalid_neg)

    # Test max length
    invalid_len = base_data.copy()
    invalid_len["length"] = 20000
    with pytest.raises(IBeamGeometryError, match="Length.*exceeds max"):
        IBeamValidator.validate(invalid_len)

    # Test min depth
    invalid_depth = base_data.copy()
    invalid_depth["total_depth"] = 10
    with pytest.raises(IBeamGeometryError, match="Total depth below minimum limit"):
        IBeamValidator.validate(invalid_depth)

def test_ibeam_validator_ratios():
    """Test I-Beam engineering ratio validations."""
    base_data = {
        "length": 1000,
        "total_depth": 300,
        "flange_width": 150,
        "web_thickness": 8,
        "flange_thickness": 12
    }

    # Web thickness too large for flange width
    invalid_web = base_data.copy()
    invalid_web["web_thickness"] = 160
    with pytest.raises(IBeamGeometryError, match="Web thickness must be less than flange width"):
        IBeamValidator.validate(invalid_web)

    # Flange thickness too large for depth
    invalid_flange = base_data.copy()
    invalid_flange["flange_thickness"] = 160
    with pytest.raises(IBeamGeometryError, match="Combined flange thickness must be less than total depth"):
        IBeamValidator.validate(invalid_flange)

def test_column_validator_schema():
    """Test Column schema validation."""
    with pytest.raises(ColumnSchemaError, match="width and height required"):
        ColumnValidator.validate({"width": 200})
        
    with pytest.raises(ColumnSchemaError, match="width and height must be numeric values"):
        ColumnValidator.validate({"width": "200", "height": 200})

def test_column_validator_geometry():
    """Test Column geometry validation (absolute limits)."""
    # Test min width
    with pytest.raises(ColumnGeometryError, match="below minimum"):
        ColumnValidator.validate({"width": 50, "height": 200})
    
    # Test max height
    with pytest.raises(ColumnGeometryError, match="exceeds maximum"):
        ColumnValidator.validate({"width": 200, "height": 4000})

def test_column_validator_ratios():
    """Test Column aspect ratio validations."""
    # Too tall/thin
    with pytest.raises(ColumnGeometryError, match="too tall for its width"):
        ColumnValidator.validate({"width": 100, "height": 500})
        
    # Too wide/short
    with pytest.raises(ColumnGeometryError, match="too wide for its height"):
        ColumnValidator.validate({"width": 1000, "height": 200})
