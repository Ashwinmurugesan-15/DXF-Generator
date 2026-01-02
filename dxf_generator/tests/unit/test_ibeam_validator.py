"""
Unit tests for I-Beam Validator.
"""
from dxf_generator.validators.ibeam_validator import IBeamValidator

def test_valid_ibeam():
    """
    Test validation of an I-Beam with valid dimensions.
    """
    IBeamValidator.validate({
        "total_depth": 300,
        "flange_width": 150,
        "web_thickness": 8,
        "flange_thickness": 12
    })
