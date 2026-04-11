from app.db.models import Anime, AppPreferences


def test_postgres_enum_values_use_lowercase_wire_values():
    assert Anime.__table__.c.season.type.enums == ["winter", "spring", "summer", "fall", "other"]
    assert Anime.__table__.c.status.type.enums == ["unwatched", "watching", "completed"]
    assert AppPreferences.__table__.c.last_used_season.type.enums == ["winter", "spring", "summer", "fall", "other"]
