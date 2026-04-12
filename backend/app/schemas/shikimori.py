from datetime import datetime, date

from pydantic import Field, field_validator

from app.schemas.common import APIModel


class ShikimoriCacheMeta(APIModel):
    source: str
    expires_at: datetime | None = None
    stale: bool = False


class ShikimoriInfo(APIModel):
    russian: str | None = None
    japanese: str | None = None
    score: str | None = None
    episodes: int | None = None
    aired_on: date | None = None
    fansubbers: list[str] = Field(default_factory=list)
    studios: list[str] = Field(default_factory=list)
    genres: list[str] = Field(default_factory=list)
    description: str | None = None

    @field_validator("score", mode="before")
    @classmethod
    def normalize_score(cls, value: object) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, int | float):
            return str(value)
        return str(value)


class ShikimoriInfoResponse(APIModel):
    anime_id: int
    search_key: str
    cache: ShikimoriCacheMeta
    result: ShikimoriInfo
