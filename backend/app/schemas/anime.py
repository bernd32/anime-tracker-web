from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints, model_validator

from app.db.models import AnimeSeason, AnimeStatus
from app.schemas.common import APIModel, ScopeInfo


TrimmedString = Annotated[str, StringConstraints(strip_whitespace=True)]


class AnimeBase(APIModel):
    name: TrimmedString = Field(min_length=1, max_length=255)
    year: int = Field(ge=1960, le=2100)
    season: AnimeSeason = AnimeSeason.OTHER
    status: AnimeStatus = AnimeStatus.UNWATCHED
    type: TrimmedString = Field(default="", max_length=100)
    comment: str = Field(default="", max_length=10_000)
    url: TrimmedString = Field(default="", max_length=2048)
    downloaded: bool = False


class AnimeCreateRequest(AnimeBase):
    pass


class AnimeUpdateRequest(APIModel):
    name: TrimmedString | None = Field(default=None, min_length=1, max_length=255)
    year: int | None = Field(default=None, ge=1960, le=2100)
    season: AnimeSeason | None = None
    status: AnimeStatus | None = None
    type: TrimmedString | None = Field(default=None, max_length=100)
    comment: str | None = Field(default=None, max_length=10_000)
    url: TrimmedString | None = Field(default=None, max_length=2048)
    downloaded: bool | None = None

    @model_validator(mode="after")
    def ensure_any_field(self) -> "AnimeUpdateRequest":
        if not any(getattr(self, field) is not None for field in self.model_fields):
            raise ValueError("At least one field must be provided.")
        return self


class AnimeStatusUpdateRequest(APIModel):
    status: AnimeStatus


class AnimeDownloadedUpdateRequest(APIModel):
    downloaded: bool


class AnimeItem(APIModel):
    id: int
    name: str
    year: int
    season: AnimeSeason
    status: AnimeStatus
    type: str
    comment: str
    url: str
    downloaded: bool
    scope: ScopeInfo
    created_at: datetime
    updated_at: datetime


class AnimeResponse(APIModel):
    item: AnimeItem


class AnimeListMeta(APIModel):
    total: int
    scope: ScopeInfo
    search: str | None = None


class AnimeListResponse(APIModel):
    items: list[AnimeItem]
    meta: AnimeListMeta


class AnimeListQuery(APIModel):
    scope_kind: str = Field(default="all")
    scope_year: int | None = Field(default=None, ge=1960, le=2100)
    season: AnimeSeason | None = None
    search: str | None = Field(default=None, max_length=255)
    status: AnimeStatus | None = None
    downloaded: bool | None = None


class RandomPickResponse(APIModel):
    item: AnimeItem | None
    meta: dict[str, object]
