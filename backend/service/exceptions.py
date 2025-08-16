# backend/service/exceptions.py

class DuplicateError(RuntimeError):
    """Raised when a unique constraint is violated during record creation."""
    pass

class NotFoundError(RuntimeError):
    """Raised when a requested resource is not found."""
    pass

class BusinessLogicError(RuntimeError):
    """Raised for general business logic failures, such as a failed sync with an external service."""
    pass