import base64
import hashlib
import hmac
import json
import secrets
import time
from collections import deque
from dataclasses import dataclass, field
from math import ceil
from threading import Lock

from fastapi import Request, Response

from app.core.config import Settings
from app.core.exceptions import ForbiddenError, TooManyRequestsError

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


@dataclass(slots=True)
class FailedLoginState:
    attempts: deque[float] = field(default_factory=deque)
    blocked_until: float = 0.0


class LoginThrottle:
    def __init__(self) -> None:
        self._states: dict[str, FailedLoginState] = {}
        self._lock = Lock()
        self._operation_count = 0

    def ensure_allowed(self, settings: Settings, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            self._operation_count += 1
            self._cleanup_stale_states(settings, now)
            state = self._states.get(key)
            if state is None:
                return
            self._prune_attempts(state, settings, now)
            if state.blocked_until > now:
                raise TooManyRequestsError(
                    code="login_rate_limited",
                    message="Too many failed login attempts. Try again later.",
                    details={"retry_after_seconds": ceil(state.blocked_until - now)},
                )
            if not state.attempts:
                self._states.pop(key, None)

    def register_failure(self, settings: Settings, key: str) -> None:
        now = time.monotonic()
        with self._lock:
            self._operation_count += 1
            self._cleanup_stale_states(settings, now)
            state = self._states.setdefault(key, FailedLoginState())
            self._prune_attempts(state, settings, now)
            state.attempts.append(now)
            if len(state.attempts) < settings.auth_login_max_failures:
                return
            state.attempts.clear()
            state.blocked_until = now + settings.auth_login_lockout_seconds
            raise TooManyRequestsError(
                code="login_rate_limited",
                message="Too many failed login attempts. Try again later.",
                details={"retry_after_seconds": settings.auth_login_lockout_seconds},
            )

    def reset(self, key: str) -> None:
        with self._lock:
            self._states.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._states.clear()
            self._operation_count = 0

    def _prune_attempts(self, state: FailedLoginState, settings: Settings, now: float) -> None:
        cutoff = now - settings.auth_login_window_seconds
        while state.attempts and state.attempts[0] <= cutoff:
            state.attempts.popleft()
        if state.blocked_until <= now and not state.attempts:
            state.blocked_until = 0.0

    def _cleanup_stale_states(self, settings: Settings, now: float) -> None:
        if self._operation_count % 32 != 0:
            return
        stale_after = now - max(settings.auth_login_window_seconds, settings.auth_login_lockout_seconds)
        for key, state in list(self._states.items()):
            self._prune_attempts(state, settings, now)
            latest_attempt = state.attempts[-1] if state.attempts else 0.0
            if state.blocked_until <= now and latest_attempt <= stale_after:
                self._states.pop(key, None)


_login_throttle = LoginThrottle()


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


def assert_login_not_rate_limited(settings: Settings, request: Request, username: str) -> None:
    _login_throttle.ensure_allowed(settings, login_throttle_key(request, username))


def record_failed_login(settings: Settings, request: Request, username: str) -> None:
    _login_throttle.register_failure(settings, login_throttle_key(request, username))


def reset_failed_logins(request: Request, username: str) -> None:
    _login_throttle.reset(login_throttle_key(request, username))


def reset_login_throttle() -> None:
    _login_throttle.clear()


def login_throttle_key(request: Request, username: str) -> str:
    return f"{_client_identity(request)}:{username.strip().lower()}"


def _client_identity(request: Request) -> str:
    client_host = (request.client.host if request.client else "").strip()
    if client_host in {"127.0.0.1", "::1", "localhost"}:
        forwarded_for = request.headers.get("x-forwarded-for", "")
        if forwarded_for:
            forwarded_host = forwarded_for.split(",", 1)[0].strip()
            if forwarded_host:
                return forwarded_host
        real_ip = request.headers.get("x-real-ip", "").strip()
        if real_ip:
            return real_ip
    return client_host or "unknown"


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
