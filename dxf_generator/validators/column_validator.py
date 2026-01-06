
from dxf_generator.exceptions.schema import ColumnSchemaError
from dxf_generator.exceptions.geometry import ColumnGeometryError
from dxf_generator.config.tolerances import (
    MAX_COLUMN_WIDTH_MM,
    MAX_COLUMN_HEIGHT_MM,
    MIN_COLUMN_WIDTH_MM,
    MIN_COLUMN_HEIGHT_MM,
    MAX_COLUMN_ASPECT_RATIO,
    MIN_COLUMN_ASPECT_RATIO
)

class ColumnValidator:
    """
    Enforces engineering constraints for Column components.
    """

    @classmethod
    def validate(cls, data: dict):
        """
        Runs the full validation suite: Schema -> Geometry -> Ratios.
        """
        cls._validate_schema(data)
        cls._validate_geometry(data)
        cls._validate_ratio(data)

    @staticmethod
    def _validate_schema(data: dict):
        # Ensure all required fields are present and numeric
        if "width" not in data or "height" not in data:
            raise ColumnSchemaError("width and height required")
        
        if not isinstance(data["width"], (int, float)) or not isinstance(data["height"], (int, float)):
            raise ColumnSchemaError("width and height must be numeric values")

    @staticmethod
    def _validate_geometry(data: dict):
        # 1. Positive value check
        if data["width"] <= 0 or data["height"] <= 0:
            raise ColumnGeometryError("Dimensions must be positive values")
        
        # 2. Absolute size limits (Engineering constraints)
        if data["width"] < MIN_COLUMN_WIDTH_MM:
            raise ColumnGeometryError(f"Width {data['width']}mm is below minimum {MIN_COLUMN_WIDTH_MM}mm")
        
        if data["width"] > MAX_COLUMN_WIDTH_MM:
            raise ColumnGeometryError(f"Width {data['width']}mm exceeds maximum {MAX_COLUMN_WIDTH_MM}mm")
            
        if data["height"] < MIN_COLUMN_HEIGHT_MM:
            raise ColumnGeometryError(f"Height {data['height']}mm is below minimum {MIN_COLUMN_HEIGHT_MM}mm")
            
        if data["height"] > MAX_COLUMN_HEIGHT_MM:
            raise ColumnGeometryError(f"Height {data['height']}mm exceeds maximum {MAX_COLUMN_HEIGHT_MM}mm")

    @staticmethod
    def _validate_ratio(data: dict):
        # Check aspect ratio to ensure structural stability
        aspect_ratio = data["height"] / data["width"]
        
        if aspect_ratio > MAX_COLUMN_ASPECT_RATIO:
            raise ColumnGeometryError(f"Column is too tall for its width (Ratio: {aspect_ratio:.2f} > {MAX_COLUMN_ASPECT_RATIO})")
            
        if aspect_ratio < MIN_COLUMN_ASPECT_RATIO:
            raise ColumnGeometryError(f"Column is too wide for its height (Ratio: {aspect_ratio:.2f} < {MIN_COLUMN_ASPECT_RATIO})")
