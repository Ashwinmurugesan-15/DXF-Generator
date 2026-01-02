
from dxf_generator.exceptions.schema import ColumnSchemaError
from dxf_generator.exceptions.geometry import ColumnGeometryError

class ColumnValidator:

    @staticmethod
    def validate(data: dict):

        # Validate schema: Check for required keys
        if "width" not in data or "height" not in data:
            raise ColumnSchemaError("width and height required")

        # Validate geometry: Check absolute limits
        if data["width"] <= 0 or data["height"] <= 0:
            raise ColumnGeometryError("Invalid column dimensions")
