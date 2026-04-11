from datetime import UTC, datetime

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
        time=datetime.now(UTC),
    )


@router.get("/readyz", response_model=HealthResponse)
def readyz() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
        time=datetime.now(UTC),
    )
