from fastapi import APIRouter, Depends

from app.api.deps import get_preferences_service, require_owner_write_access
from app.schemas.preferences import PreferencesResponse, PreferencesUpdateRequest
from app.services.preferences import PreferencesService

router = APIRouter()


@router.get("", response_model=PreferencesResponse)
def get_preferences(service: PreferencesService = Depends(get_preferences_service)) -> PreferencesResponse:
    return service.get_preferences()


@router.patch("", response_model=PreferencesResponse)
def update_preferences(
    payload: PreferencesUpdateRequest,
    service: PreferencesService = Depends(get_preferences_service),
    _: None = Depends(require_owner_write_access),
) -> PreferencesResponse:
    return service.update_preferences(payload)
