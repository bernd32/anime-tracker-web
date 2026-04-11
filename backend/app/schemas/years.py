from app.schemas.common import APIModel


class YearListItem(APIModel):
    year: int
    has_entries: bool
    has_scaffold: bool
    counts: dict[str, int]


class YearListResponse(APIModel):
    items: list[YearListItem]


class YearScaffoldResponse(APIModel):
    year: int
    created: bool
    seasons: list[str]


class DeleteYearResponse(APIModel):
    year: int
    deleted_anime_count: int
    deleted_scaffold: bool
