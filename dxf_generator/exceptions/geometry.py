from .base import DXFValidationError

class IBeamGeometryError(DXFValidationError):
    """Raised when I-Beam geometry is invalid"""
    pass

class ColumnGeometryError(DXFValidationError):
    """Raised when column geometry is invalid"""
    pass
