import re
import unicodedata

from app.db.models import AnimeSeason

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value or "")
    normalized = _WHITESPACE_RE.sub(" ", normalized.strip())
    return normalized.casefold()


def normalize_text(value: str | None) -> str:
    return (value or "").strip()


def normalize_comment(value: str | None) -> str:
    return (value or "").strip()


def normalize_season(raw: str | None, year: int) -> AnimeSeason:
    if year < 2010:
        return AnimeSeason.OTHER
    value = (raw or "other").strip().lower()
    mapping = {
        "": AnimeSeason.OTHER,
        "other": AnimeSeason.OTHER,
        "winter": AnimeSeason.WINTER,
        "spring": AnimeSeason.SPRING,
        "summer": AnimeSeason.SUMMER,
        "fall": AnimeSeason.FALL,
        "autumn": AnimeSeason.FALL,
    }
    return mapping.get(value, AnimeSeason.OTHER)


def scope_kind_for_year(year: int) -> str:
    return "pre2010" if year < 2010 else "year"
