"""Student Management System package."""
from .services import StudentManager
from .errors import SMSError, ValidationError, NotFoundError, DuplicateError

__all__ = ["StudentManager", "SMSError", "ValidationError",
           "NotFoundError", "DuplicateError"]
__version__ = "1.0.0"
