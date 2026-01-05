import pytest
from dxf_generator.domain.ibeam import IBeam
from dxf_generator.exceptions.geometry import IBeamGeometryError

def test_ibeam_creation_success():
    """Test successful creation of an I-Beam."""
    ibeam = IBeam(total_depth=300, flange_width=150, web_thickness=8, flange_thickness=12)
    assert ibeam.data["total_depth"] == 300
    assert ibeam.data["flange_width"] == 150

def test_ibeam_creation_failure_invalid_dimensions():
    """Test I-Beam creation failure with invalid dimensions."""
    with pytest.raises(IBeamGeometryError):
        # Web thickness cannot be greater than flange width
        IBeam(total_depth=300, flange_width=150, web_thickness=200, flange_thickness=12)

def test_ibeam_creation_failure_negative_values():
    """Test I-Beam creation failure with negative values."""
    with pytest.raises(IBeamGeometryError):
        IBeam(total_depth=-300, flange_width=150, web_thickness=8, flange_thickness=12)

def test_ibeam_ratio_validation_flange_thickness():
    """Test flange thickness to width ratio validation."""
    with pytest.raises(IBeamGeometryError) as excinfo:
        # 40 / 150 = 0.266... (> 0.20)
        # depth=500, web=15 (ratio 0.03 > 0.02)
        IBeam(total_depth=500, flange_width=150, web_thickness=15, flange_thickness=40)
    assert "Flange thickness" in str(excinfo.value)
    assert "is too large for the flange width" in str(excinfo.value)

def test_ibeam_ratio_validation_web_thickness():
    """Test web thickness to width ratio validation."""
    with pytest.raises(IBeamGeometryError) as excinfo:
        # 50 / 150 = 0.333... (> 0.25)
        IBeam(total_depth=500, flange_width=150, web_thickness=50, flange_thickness=10)
    assert "Web thickness" in str(excinfo.value)
    assert "is too large for the flange width" in str(excinfo.value)
