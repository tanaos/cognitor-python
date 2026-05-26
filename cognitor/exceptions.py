from __future__ import annotations


class CognitorError(Exception):
    """Base exception for all Cognitor client errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(CognitorError):
    """Raised when the server rejects the request due to missing or invalid credentials (HTTP 401)."""


class NotFoundError(CognitorError):
    """Raised when the requested resource does not exist (HTTP 404)."""


class ConflictError(CognitorError):
    """Raised when the operation conflicts with existing state, e.g. duplicate collection (HTTP 409)."""


class ValidationError(CognitorError):
    """Raised when the server rejects the request due to invalid input (HTTP 400 / 422)."""


class ServerError(CognitorError):
    """Raised on unhandled server-side errors (HTTP 5xx)."""
