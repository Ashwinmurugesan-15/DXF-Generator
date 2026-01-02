
from .base_component import BaseComponent
# Import IBeamValidator for validation
from dxf_generator.validators.ibeam_validator import IBeamValidator
# Import DXFDrawing for generating drawings
from dxf_generator.drawing.drawing import DXFDrawing

class IBeam(BaseComponent):

    def __init__(self, total_depth, flange_width, web_thickness, flange_thickness):

        # Store I-Beam dimensions in data dictionary
        self.data = {
            "total_depth": total_depth,
            "flange_width": flange_width,
            "web_thickness": web_thickness,
            "flange_thickness": flange_thickness
        }

        # 🔒 Validation enforced at library level
        IBeamValidator.validate(self.data)

    def generate_dxf(self, filepath: str):
        # Create a new DXF drawing instance
        drawing = DXFDrawing()
        # Draw the I-Beam geometry
        drawing.draw_ibeam(self.data)
        # Save the drawing to the specified file
        drawing.save(filepath)