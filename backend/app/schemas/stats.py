from app.schemas.common import APIModel


class Totals(APIModel):
    total: int
    completed: int
    completion_percent: float


class TypeCount(APIModel):
    type: str
    count: int


class YearStats(APIModel):
    year: int
    total: int
    completed: int


class ScopeTotals(APIModel):
    total: int
    completed: int


class ScopeStats(APIModel):
    pre2010: ScopeTotals
    years: list[YearStats]


class StatsResponse(APIModel):
    totals: Totals
    by_status: dict[str, int]
    by_type: list[TypeCount]
    by_scope: ScopeStats
