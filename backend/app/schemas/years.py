from app.schemas.common import APIModel


class YearListItem(APIModel):
    year: int
    has_entries: bool
    counts: dict[str, int]


class YearListResponse(APIModel):
    items: list[YearListItem]


class DeleteYearResponse(APIModel):
    year: int
    deleted_anime_count: int
