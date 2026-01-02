
from .base import DXFValidationError

class IBeamSchemaError(DXFValidationError):
    """Raised when I-Beam schema is invalid"""
    pass

class ColumnSchemaError(DXFValidationError):
    """Raised when column schema is invalid"""
    pass
