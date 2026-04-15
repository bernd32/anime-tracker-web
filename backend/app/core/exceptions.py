from collections.abc import Mapping
from http import HTTPStatus
from typing import Any


class AppError(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = dict(details or {})
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, *, message: str = "Resource not found", details: Mapping[str, Any] | None = None) -> None:
        super().__init__(
            code="not_found",
            message=message,
            status_code=HTTPStatus.NOT_FOUND,
            details=details,
        )


class ConflictError(AppError):
    def __init__(self, *, code: str = "conflict", message: str, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(
            code=code,
            message=message,
            status_code=HTTPStatus.CONFLICT,
            details=details,
        )


class ValidationAppError(AppError):
    def __init__(self, *, message: str, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(
            code="validation_error",
            message=message,
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            details=details,
        )


class UnauthorizedError(AppError):
    def __init__(
        self,
        *,
        code: str = "unauthorized",
        message: str = "Authentication required.",
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED,
            details=details,
        )


class ForbiddenError(AppError):
    def __init__(
        self,
        *,
        code: str = "forbidden",
        message: str = "You do not have permission to perform this action.",
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            status_code=HTTPStatus.FORBIDDEN,
            details=details,
        )


class ExternalServiceError(AppError):
    def __init__(self, *, message: str, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(
            code="external_service_error",
            message=message,
            status_code=HTTPStatus.BAD_GATEWAY,
            details=details,
        )
