"""HTTP-facing errors raised from services (routes translate to responses)."""

from __future__ import annotations

from fastapi import HTTPException, status


class AppError(HTTPException):
    """Base application error with structured camelCase body for clients."""

    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
    ) -> None:
        super().__init__(status_code=status_code, detail={"code": code, "message": message})


class NotFoundError(AppError):
    """Entity missing or wrong tenant scope."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, code="NOT_FOUND", message=message)


class ConflictError(AppError):
    """Unique constraint or business conflict."""

    def __init__(self, message: str = "Conflict") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, code="CONFLICT", message=message)


class UnauthorizedError(AppError):
    """Missing or invalid credentials."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, code="UNAUTHORIZED", message=message)


class ForbiddenError(AppError):
    """Authenticated but not allowed."""

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, code="FORBIDDEN", message=message)


_UNPROCESSABLE = getattr(
    status,
    "HTTP_422_UNPROCESSABLE_CONTENT",
    status.HTTP_422_UNPROCESSABLE_ENTITY,
)


class ValidationAppError(AppError):
    """Business rule failed after Pydantic layer (rare; prefer request models)."""

    def __init__(self, message: str) -> None:
        super().__init__(
            status_code=_UNPROCESSABLE,
            code="VALIDATION_ERROR",
            message=message,
        )
