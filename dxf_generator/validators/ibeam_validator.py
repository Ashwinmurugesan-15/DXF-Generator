# Schema-level exception
from dxf_generator.exceptions.schema import IBeamSchemaError

# Geometry-level exception
from dxf_generator.exceptions.geometry import IBeamGeometryError

# Engineering tolerances
from dxf_generator.config.tolerances import (
    MAX_IBEAM_LENGTH_MM,
    MAX_IBEAM_WIDTH_MM,
    MAX_IBEAM_DEPTH_MM,
    MIN_IBEAM_DEPTH_MM,
    MIN_IBEAM_WIDTH_MM,
    MIN_IBEAM_WEB_THICKNESS_MM,
    MIN_IBEAM_FLANGE_THICKNESS_MM,
    MIN_WEB_TO_DEPTH_RATIO,
    MIN_WIDTH_TO_DEPTH_RATIO,
    MAX_FLANGE_THICKNESS_TO_WIDTH_RATIO,
    MAX_WEB_THICKNESS_TO_WIDTH_RATIO
)


class IBeamValidator:
    # Required parameters for an I-beam
    REQUIRED_FIELDS = [
        "length",
        "total_depth",
        "flange_width",
        "web_thickness",
        "flange_thickness"
    ]

    @classmethod
    def validate(cls, data: dict):
        cls._validate_schema(data)
        cls._validate_geometry(data)

    @staticmethod
    def _validate_schema(data: dict):
        # Validate required fields and numeric types
        for field in IBeamValidator.REQUIRED_FIELDS:
            if field not in data:
                raise IBeamSchemaError(f"Missing field: {field}")
            if not isinstance(data[field], (int, float)):
                raise IBeamSchemaError(f"{field} must be numeric")

    @staticmethod
    def _validate_geometry(data: dict):
        # Positive value checks
        for field in IBeamValidator.REQUIRED_FIELDS:
            if data[field] <= 0:
                raise IBeamGeometryError(f"{field.replace('_', ' ')} must be greater than 0")
                
        # Length validation (client explicitly asked)
        if data["length"] > MAX_IBEAM_LENGTH_MM:
            raise IBeamGeometryError(
                f"Length ({data['length']}) exceeds max {MAX_IBEAM_LENGTH_MM}mm"
            )

        # Absolute min/max limits
        if data["total_depth"] > MAX_IBEAM_DEPTH_MM:
            raise IBeamGeometryError("Total depth exceeds maximum limit")
        if data["flange_width"] > MAX_IBEAM_WIDTH_MM:
            raise IBeamGeometryError("Flange width exceeds maximum limit")

        if data["total_depth"] < MIN_IBEAM_DEPTH_MM:
            raise IBeamGeometryError("Total depth below minimum limit")
        if data["flange_width"] < MIN_IBEAM_WIDTH_MM:
            raise IBeamGeometryError("Flange width below minimum limit")
        if data["web_thickness"] < MIN_IBEAM_WEB_THICKNESS_MM:
            raise IBeamGeometryError("Web thickness below minimum limit")
        if data["flange_thickness"] < MIN_IBEAM_FLANGE_THICKNESS_MM:
            raise IBeamGeometryError("Flange thickness below minimum limit")

        # Logical geometry relationships
        if data["web_thickness"] >= data["flange_width"]:
            raise IBeamGeometryError("Web thickness must be less than flange width")

        if data["flange_thickness"] * 2 >= data["total_depth"]:
            raise IBeamGeometryError("Combined flange thickness must be less than total depth")

        # Engineering proportion rules
        if data["web_thickness"] < data["total_depth"] * MIN_WEB_TO_DEPTH_RATIO:
            raise IBeamGeometryError("Web thickness too small relative to depth")

        if data["flange_width"] < data["total_depth"] * MIN_WIDTH_TO_DEPTH_RATIO:
            raise IBeamGeometryError("Flange width too small relative to depth")

        # Added Ratio Validations
        if data["flange_thickness"] > data["flange_width"] * MAX_FLANGE_THICKNESS_TO_WIDTH_RATIO:
            raise IBeamGeometryError(f"Flange thickness ({data['flange_thickness']}) is too large for the flange width ({data['flange_width']}). Ratio must be <= {MAX_FLANGE_THICKNESS_TO_WIDTH_RATIO}")

        if data["web_thickness"] > data["flange_width"] * MAX_WEB_THICKNESS_TO_WIDTH_RATIO:
            raise IBeamGeometryError(f"Web thickness ({data['web_thickness']}) is too large for the flange width ({data['flange_width']}). Ratio must be <= {MAX_WEB_THICKNESS_TO_WIDTH_RATIO}")
