"""
Custom error classes for FastAPI backend.
Provides typed errors that can be raised in route handlers.
"""
from typing import Any, Dict, Optional


class AppError(Exception):
    """Base application error class."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AppError):
    """Authentication failed error (401 Unauthorized)."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)


class ValidationError(AppError):
    """Validation error (400 Bad Request)."""

    def __init__(
        self,
        message: str = "Validation failed",
        errors: Optional[Dict[str, list]] = None
    ):
        details = {"errors": errors} if errors else {}
        super().__init__(message, status_code=400, details=details)


class NotFoundError(AppError):
    """Resource not found error (404 Not Found)."""

    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)


class ForbiddenError(AppError):
    """Access forbidden error (403 Forbidden)."""

    def __init__(self, message: str = "Access forbidden", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)


class ConflictError(AppError):
    """Resource conflict error (409 Conflict)."""

    def __init__(self, message: str = "Resource already exists", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=409, details=details)


class RateLimitError(AppError):
    """Rate limit exceeded error (429 Too Many Requests)."""

    def __init__(self, message: str = "Too many requests", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=429, details=details)


class InternalServerError(AppError):
    """Internal server error (500 Internal Server Error)."""

    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)
