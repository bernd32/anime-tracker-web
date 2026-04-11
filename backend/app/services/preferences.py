from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.repositories.preferences import PreferencesRepository
from app.schemas.preferences import PreferencesResponse, PreferencesUpdateRequest


class PreferencesService:
    def __init__(self, session_factory: Callable[[], AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def get_preferences(self) -> PreferencesResponse:
        with self.session_factory() as session:
            pref = PreferencesRepository(session).get_singleton()
            return PreferencesResponse.model_validate(pref)

    def update_preferences(self, payload: PreferencesUpdateRequest) -> PreferencesResponse:
        with self.session_factory() as session:
            pref = PreferencesRepository(session).get_singleton()
            for key, value in payload.model_dump(exclude_unset=True).items():
                setattr(pref, key, value)
            session.commit()
            session.refresh(pref)
            return PreferencesResponse.model_validate(pref)
