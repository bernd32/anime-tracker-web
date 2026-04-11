from urllib.parse import urlparse

from app.core.exceptions import ValidationAppError


ALLOWED_SCHEMES = {"http", "https"}


def validate_optional_url(url: str) -> str:
    candidate = url.strip()
    if not candidate:
        return ""
    parsed = urlparse(candidate)
    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.netloc:
        raise ValidationAppError(
            message="URL must be a valid HTTP or HTTPS URL.",
            details={"field": "url"},
        )
    return candidate
