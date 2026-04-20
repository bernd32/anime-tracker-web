from fastapi import APIRouter, Depends, Query, Response

from app.api.deps import (
    get_anime_service,
    get_shikimori_service,
    get_stats_service,
    require_owner_write_access,
)
from app.schemas.anime import (
    AnimeCreateRequest,
    AnimeDownloadedUpdateRequest,
    AnimeListQuery,
    AnimeListResponse,
    AnimeResponse,
    AnimeStatusUpdateRequest,
    AnimeUpdateRequest,
    RandomPickResponse,
)
from app.schemas.shikimori import ShikimoriInfoResponse
from app.schemas.stats import StatsResponse
from app.services.anime import AnimeService
from app.services.shikimori import ShikimoriService
from app.services.stats import StatsService

router = APIRouter()


@router.get("", response_model=AnimeListResponse)
def list_anime(
    scope_kind: str = Query(default="all"),
    scope_year: int | None = Query(default=None),
    season: str | None = Query(default=None),
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    downloaded: bool | None = Query(default=None),
    service: AnimeService = Depends(get_anime_service),
) -> AnimeListResponse:
    query = AnimeListQuery(
        scope_kind=scope_kind,
        scope_year=scope_year,
        season=season,
        search=search,
        status=status,
        downloaded=downloaded,
    )
    return service.list_anime(query)


@router.post("", response_model=AnimeResponse, status_code=201, dependencies=[Depends(require_owner_write_access)])
def create_anime(payload: AnimeCreateRequest, service: AnimeService = Depends(get_anime_service)) -> AnimeResponse:
    return service.create_anime(payload)


@router.get("/random-pick", response_model=RandomPickResponse)
def random_pick(
    scope_kind: str = Query(default="all"),
    scope_year: int | None = Query(default=None),
    season: str | None = Query(default=None),
    search: str | None = Query(default=None),
    service: AnimeService = Depends(get_anime_service),
) -> RandomPickResponse:
    query = AnimeListQuery(
        scope_kind=scope_kind,
        scope_year=scope_year,
        season=season,
        search=search,
    )
    return service.random_pick(query)


@router.get("/stats", response_model=StatsResponse)
def get_stats(service: StatsService = Depends(get_stats_service)) -> StatsResponse:
    return service.get_stats()


@router.get("/{anime_id}", response_model=AnimeResponse)
def get_anime(anime_id: int, service: AnimeService = Depends(get_anime_service)) -> AnimeResponse:
    return service.get_anime(anime_id)


@router.patch(
    "/{anime_id}",
    response_model=AnimeResponse,
    dependencies=[Depends(require_owner_write_access)],
)
def update_anime(
    anime_id: int,
    payload: AnimeUpdateRequest,
    service: AnimeService = Depends(get_anime_service),
) -> AnimeResponse:
    return service.update_anime(anime_id, payload)


@router.delete("/{anime_id}", status_code=204, dependencies=[Depends(require_owner_write_access)])
def delete_anime(anime_id: int, service: AnimeService = Depends(get_anime_service)) -> Response:
    service.delete_anime(anime_id)
    return Response(status_code=204)


@router.post(
    "/{anime_id}/status",
    response_model=AnimeResponse,
    dependencies=[Depends(require_owner_write_access)],
)
def update_status(
    anime_id: int,
    payload: AnimeStatusUpdateRequest,
    service: AnimeService = Depends(get_anime_service),
) -> AnimeResponse:
    return service.update_anime(anime_id, AnimeUpdateRequest(status=payload.status))


@router.post(
    "/{anime_id}/downloaded",
    response_model=AnimeResponse,
    dependencies=[Depends(require_owner_write_access)],
)
def update_downloaded(
    anime_id: int,
    payload: AnimeDownloadedUpdateRequest,
    service: AnimeService = Depends(get_anime_service),
) -> AnimeResponse:
    return service.update_anime(anime_id, AnimeUpdateRequest(downloaded=payload.downloaded))


@router.get("/{anime_id}/shikimori", response_model=ShikimoriInfoResponse)
def get_shikimori(
    anime_id: int,
    service: ShikimoriService = Depends(get_shikimori_service),
) -> ShikimoriInfoResponse:
    return service.get_info(anime_id)


@router.post(
    "/{anime_id}/shikimori/refresh",
    response_model=ShikimoriInfoResponse,
    dependencies=[Depends(require_owner_write_access)],
)
def refresh_shikimori(
    anime_id: int,
    service: ShikimoriService = Depends(get_shikimori_service),
) -> ShikimoriInfoResponse:
    return service.get_info(anime_id, force_refresh=True)


@router.delete(
    "/{anime_id}/shikimori",
    status_code=204,
    dependencies=[Depends(require_owner_write_access)],
)
def reset_shikimori_cache(
    anime_id: int,
    service: ShikimoriService = Depends(get_shikimori_service),
) -> Response:
    service.reset_cache(anime_id)
    return Response(status_code=204)
