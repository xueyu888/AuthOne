# backend/service/exceptions.py
from __future__ import annotations

class DuplicateError(RuntimeError):
    """Raised when a unique constraint is violated during record creation."""
    pass

class NotFoundError(RuntimeError):
    """Raised when a requested resource is not found."""
    pass

class ConcurrencyError(RuntimeError):
    """Raised for optimistic concurrency conflicts (e.g., StaleDataError)."""
    pass

class BusinessLogicError(RuntimeError):
    """Raised for general business logic failures, such as external sync failures."""
    pass
