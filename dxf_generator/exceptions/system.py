
from .base import DXFValidationError

class SystemLimitError(DXFValidationError):
    """Raised when a system-level limit (e.g., batch size) is exceeded"""
    pass
