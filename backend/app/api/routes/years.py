from fastapi import APIRouter, Depends

from app.api.deps import get_year_service
from app.schemas.years import DeleteYearResponse, YearListResponse
from app.services.years import YearService

router = APIRouter()


@router.get("", response_model=YearListResponse)
def list_years(service: YearService = Depends(get_year_service)) -> YearListResponse:
    return service.list_years()


@router.delete("/{year}", response_model=DeleteYearResponse)
def delete_year(year: int, service: YearService = Depends(get_year_service)) -> DeleteYearResponse:
    return service.delete_year(year)
