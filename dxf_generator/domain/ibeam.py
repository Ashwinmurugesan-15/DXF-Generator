from .base_component import BaseComponent
from dxf_generator.validators.ibeam_validator import IBeamValidator
from dxf_generator.drawing.drawing import DXFDrawing


class IBeam(BaseComponent):
    """
    I-Beam domain object.
    Validation is enforced at library level.
    """

    def __init__(self, total_depth, flange_width, web_thickness, flange_thickness, length=1000):
        # Store I-Beam dimensions
        self.data = {
            "length": length,
            "total_depth": total_depth,
            "flange_width": flange_width,
            "web_thickness": web_thickness,
            "flange_thickness": flange_thickness
        }

        # 🔒 Enforce validation immediately (client requirement)
        IBeamValidator.validate(self.data)

    def generate_dxf(self, filepath: str):
        # Create DXF drawing
        drawing = DXFDrawing()

        # Draw I-Beam geometry
        drawing.draw_ibeam(self.data)

        # Save DXF file
        drawing.save(filepath)
