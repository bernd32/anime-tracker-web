from sqlalchemy.orm import Session

from app.db.models import AppPreferences


class PreferencesRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_singleton(self) -> AppPreferences:
        pref = self.session.get(AppPreferences, 1)
        if pref is None:
            pref = AppPreferences(id=1)
            self.session.add(pref)
            self.session.flush()
            self.session.refresh(pref)
        return pref
