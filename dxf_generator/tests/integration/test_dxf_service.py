"""
Integration tests for DXF Service.
"""
from dxf_generator.domain.ibeam import IBeam
from dxf_generator.services.dxf_service import DXFService

def test_dxf_generation():
    """
    Test that the DXFService can generate a file for an I-Beam component.
    """
    ibeam = IBeam(300, 150, 8, 12)
    DXFService.save(ibeam, "test_ibeam.dxf")
