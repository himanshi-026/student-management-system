"""Custom exceptions so the UI can show friendly messages."""


class SMSError(Exception):
    """Base class for all application errors."""


class ValidationError(SMSError):
    """Input failed validation."""


class NotFoundError(SMSError):
    """Requested record does not exist."""


class DuplicateError(SMSError):
    """Record already exists."""
