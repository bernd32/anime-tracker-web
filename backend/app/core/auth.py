import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass

from fastapi import Response

from app.core.config import Settings
from app.core.exceptions import ForbiddenError

SESSION_COOKIE_NAME = "anime_tracker_session"
CSRF_COOKIE_NAME = "anime_tracker_csrf"
CSRF_HEADER_NAME = "X-CSRF-Token"
_COOKIE_SAMESITE = "lax"


@dataclass(frozen=True)
class OwnerSession:
    username: str
    csrf_token: str
    issued_at: int
    expires_at: int


def verify_owner_credentials(settings: Settings, username: str, password: str) -> bool:
    return secrets.compare_digest(username, settings.auth_owner_username) and secrets.compare_digest(
        password, settings.auth_owner_password
    )


def create_owner_session_token(settings: Settings) -> tuple[str, OwnerSession]:
    issued_at = int(time.time())
    expires_at = issued_at + settings.auth_session_max_age_seconds
    session = OwnerSession(
        username=settings.auth_owner_username,
        csrf_token=secrets.token_urlsafe(32),
        issued_at=issued_at,
        expires_at=expires_at,
    )
    payload = {
        "sub": session.username,
        "csrf": session.csrf_token,
        "iat": session.issued_at,
        "exp": session.expires_at,
        "v": 1,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.digest(_signing_key(settings), payload_bytes, hashlib.sha256)
    token = f"{_b64encode(payload_bytes)}.{_b64encode(signature)}"
    return token, session


def read_owner_session(token: str | None, settings: Settings) -> OwnerSession | None:
    if not token or "." not in token:
        return None

    payload_part, signature_part = token.split(".", 1)
    try:
        payload_bytes = _b64decode(payload_part)
        actual_signature = _b64decode(signature_part)
        expected_signature = hmac.digest(_signing_key(settings), payload_bytes, hashlib.sha256)
        if not secrets.compare_digest(actual_signature, expected_signature):
            return None
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (ValueError, TypeError, json.JSONDecodeError):
        return None

    try:
        username = str(payload["sub"])
        csrf_token = str(payload["csrf"])
        issued_at = int(payload["iat"])
        expires_at = int(payload["exp"])
    except (KeyError, TypeError, ValueError):
        return None

    if username != settings.auth_owner_username:
        return None
    if expires_at <= int(time.time()):
        return None
    if not csrf_token:
        return None

    return OwnerSession(
        username=username,
        csrf_token=csrf_token,
        issued_at=issued_at,
        expires_at=expires_at,
    )


def set_auth_cookies(response: Response, settings: Settings, session_token: str, session: OwnerSession) -> None:
    cookie_options = {
        "max_age": settings.auth_session_max_age_seconds,
        "path": "/",
        "secure": settings.auth_cookie_secure,
        "samesite": _COOKIE_SAMESITE,
    }
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_token,
        httponly=True,
        **cookie_options,
    )
    response.set_cookie(
        CSRF_COOKIE_NAME,
        session.csrf_token,
        httponly=False,
        **cookie_options,
    )


def clear_auth_cookies(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        SESSION_COOKIE_NAME,
        path="/",
        secure=settings.auth_cookie_secure,
        httponly=True,
        samesite=_COOKIE_SAMESITE,
    )
    response.delete_cookie(
        CSRF_COOKIE_NAME,
        path="/",
        secure=settings.auth_cookie_secure,
        httponly=False,
        samesite=_COOKIE_SAMESITE,
    )


def validate_csrf(session: OwnerSession, csrf_cookie: str | None, csrf_header: str | None) -> None:
    if not csrf_cookie or not csrf_header:
        raise ForbiddenError(
            code="csrf_missing",
            message="A valid CSRF token is required for write requests.",
        )
    if not secrets.compare_digest(csrf_cookie, session.csrf_token) or not secrets.compare_digest(
        csrf_header, session.csrf_token
    ):
        raise ForbiddenError(
            code="csrf_invalid",
            message="The CSRF token is invalid.",
        )


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}".encode("ascii"))


def _signing_key(settings: Settings) -> bytes:
    return hmac.digest(
        settings.auth_session_secret.encode("utf-8"),
        settings.auth_owner_password.encode("utf-8"),
        hashlib.sha256,
    )
