
# Import schema-level exception for missing/invalid fields
from dxf_generator.exceptions.schema import IBeamSchemaError

# Import geometry-level exception for dimension limit violations
from dxf_generator.exceptions.geometry import IBeamGeometryError

# Import engineering tolerance limits for I-Beam dimensions
from dxf_generator.config.tolerances import (
    MAX_IBEAM_WIDTH_MM,
    MAX_IBEAM_DEPTH_MM,
    MIN_IBEAM_DEPTH_MM,
    MIN_IBEAM_WIDTH_MM,
    MIN_IBEAM_WEB_THICKNESS_MM,
    MIN_IBEAM_FLANGE_THICKNESS_MM
)


class IBeamValidator:

    # Mandatory fields required to define an I-Beam
    REQUIRED_FIELDS = ["total_depth", "flange_width", "web_thickness", "flange_thickness"]

    # Maximum allowed engineering limits for I-Beam dimensions
    LIMITS = {
        "width": MAX_IBEAM_WIDTH_MM,
        "depth": MAX_IBEAM_DEPTH_MM
    }

    @classmethod
    def validate(cls, data: dict):
        # Entry point to perform schema and geometry validation
        cls._validate_schema(data)
        cls._validate_geometry(data)

    @staticmethod
    def _validate_schema(data: dict):
        # Validate presence and numeric type of required fields
        for field in IBeamValidator.REQUIRED_FIELDS:
            # Check if field exists
            if field not in data:
                raise IBeamSchemaError(f"Missing field: {field}")
            # Ensure field is a number
            if not isinstance(data[field], (int, float)):
                raise IBeamSchemaError(f"{field} must be numeric")

    @staticmethod
    def _validate_geometry(data: dict):
        # Simple geometric validation for I-Beam
        if data["web_thickness"] >= data["flange_width"]:
            raise IBeamGeometryError(f"Web thickness ({data['web_thickness']}) must be less than flange width ({data['flange_width']})")
        if data["flange_thickness"] * 2 >= data["total_depth"]:
            raise IBeamGeometryError(f"Total flange thickness ({data['flange_thickness'] * 2}) must be less than total depth ({data['total_depth']})")
        
        # Validate against maximum limits
        if data["total_depth"] > IBeamValidator.LIMITS["depth"]:
            raise IBeamGeometryError(f"Depth ({data['total_depth']}) exceeds maximum limit of {IBeamValidator.LIMITS['depth']}mm")
        if data["flange_width"] > IBeamValidator.LIMITS["width"]:
            raise IBeamGeometryError(f"Flange width ({data['flange_width']}) exceeds maximum limit of {IBeamValidator.LIMITS['width']}mm")

        # Validate against minimum limits
        if data["total_depth"] < MIN_IBEAM_DEPTH_MM:
            raise IBeamGeometryError(f"Depth ({data['total_depth']}) is below minimum of {MIN_IBEAM_DEPTH_MM}mm")
        if data["flange_width"] < MIN_IBEAM_WIDTH_MM:
            raise IBeamGeometryError(f"Flange width ({data['flange_width']}) is below minimum of {MIN_IBEAM_WIDTH_MM}mm")
        if data["web_thickness"] < MIN_IBEAM_WEB_THICKNESS_MM:
            raise IBeamGeometryError(f"Web thickness ({data['web_thickness']}) is below minimum of {MIN_IBEAM_WEB_THICKNESS_MM}mm")
        if data["flange_thickness"] < MIN_IBEAM_FLANGE_THICKNESS_MM:
            raise IBeamGeometryError(f"Flange thickness ({data['flange_thickness']}) is below minimum of {MIN_IBEAM_FLANGE_THICKNESS_MM}mm")

        for field in IBeamValidator.REQUIRED_FIELDS:
            if data[field] <= 0:
                raise IBeamGeometryError(f"{field.replace('_', ' ')} must be greater than 0")
