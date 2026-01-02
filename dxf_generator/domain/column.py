
from .base_component import BaseComponent
# Import ColumnValidator for validation
from dxf_generator.validators.column_validator import ColumnValidator
# Import DXFDrawing for generating drawings
from dxf_generator.drawing.drawing import DXFDrawing

class Column(BaseComponent):

    def __init__(self, width, height):

        # Store column dimensions in data dictionary
        self.data = {
            "width": width,
            "height": height
        }

        # 🔒 Mandatory validation
        ColumnValidator.validate(self.data)

    def generate_dxf(self, filepath: str):
        # Create a new DXF drawing instance
        drawing = DXFDrawing()
        # Draw the column geometry
        drawing.draw_column(self.data)
        # Save the drawing to the specified file
        drawing.save(filepath)
