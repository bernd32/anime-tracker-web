from typing import Literal

from pydantic import Field

from app.db.models import AnimeSeason
from app.schemas.common import APIModel


class PreferencesResponse(APIModel):
    last_scope_kind: Literal["year", "pre2010", "all"] = "year"
    last_scope_year: int | None = Field(default=None, ge=1960, le=2100)
    last_used_season: AnimeSeason | None = None


class PreferencesUpdateRequest(APIModel):
    last_scope_kind: Literal["year", "pre2010", "all"] | None = None
    last_scope_year: int | None = Field(default=None, ge=1960, le=2100)
    last_used_season: AnimeSeason | None = None
