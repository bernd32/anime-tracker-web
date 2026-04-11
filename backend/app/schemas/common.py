from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import AnimeSeason, AnimeStatus


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class ScopeInfo(APIModel):
    kind: Literal["all", "pre2010", "year"]
    year: int | None = None


class ErrorBody(APIModel):
    code: str
    message: str
    details: dict[str, object] = Field(default_factory=dict)
    request_id: str | None = None


class ErrorResponse(APIModel):
    error: ErrorBody


class HealthResponse(APIModel):
    status: Literal["ok"]
    service: str
    environment: str
    time: datetime


__all__ = [
    "APIModel",
    "AnimeSeason",
    "AnimeStatus",
    "ErrorBody",
    "ErrorResponse",
    "HealthResponse",
    "ScopeInfo",
]
