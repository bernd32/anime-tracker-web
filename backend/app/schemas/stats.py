from app.schemas.common import APIModel


class TypeCount(APIModel):
    type: str
    count: int


class YearStats(APIModel):
    year: int
    total: int
    completed: int


class StatsResponse(APIModel):
    totals: dict[str, float | int]
    by_status: dict[str, int]
    by_type: list[TypeCount]
    by_scope: dict[str, object]
