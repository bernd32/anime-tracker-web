from collections.abc import Sequence
import logging
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError
from app.schemas.common import ErrorBody, ErrorResponse

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str:
    request_id = request.headers.get("x-request-id") or str(uuid4())
    request.state.request_id = request_id
    return request_id


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    request_id = _request_id(request)
    payload = ErrorResponse(
        error=ErrorBody(code=exc.code, message=exc.message, details=exc.details, request_id=request_id)
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump(mode="json"))


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = _request_id(request)
    payload = ErrorResponse(
        error=ErrorBody(
            code="validation_error",
            message="Request validation failed.",
            details={"errors": exc.errors()},
            request_id=request_id,
        )
    )
    return JSONResponse(status_code=422, content=payload.model_dump(mode="json"))


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = _request_id(request)
    logger.exception("Unhandled application error", extra={"request_id": request_id, "path": str(request.url.path)})
    payload = ErrorResponse(
        error=ErrorBody(
            code="internal_error",
            message="An unexpected error occurred.",
            details={},
            request_id=request_id,
        )
    )
    return JSONResponse(status_code=500, content=payload.model_dump(mode="json"))


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
