from fastapi import APIRouter, Depends, Response, status

from app.api.deps import get_optional_owner_session
from app.core.auth import (
    OwnerSession,
    clear_auth_cookies,
    create_owner_session_token,
    set_auth_cookies,
    verify_owner_credentials,
)
from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError
from app.schemas.auth import AuthSessionResponse, LoginRequest

router = APIRouter()


@router.get("/session", response_model=AuthSessionResponse)
def get_session(owner_session: OwnerSession | None = Depends(get_optional_owner_session)) -> AuthSessionResponse:
    return _session_response(owner_session)


@router.post("/login", response_model=AuthSessionResponse)
def login(payload: LoginRequest, response: Response) -> AuthSessionResponse:
    settings = get_settings()
    if not verify_owner_credentials(settings, payload.username, payload.password):
        raise UnauthorizedError(
            code="authentication_failed",
            message="Invalid username or password.",
        )

    session_token, owner_session = create_owner_session_token(settings)
    set_auth_cookies(response, settings, session_token, owner_session)
    return _session_response(owner_session)


@router.post("/logout", response_model=AuthSessionResponse, status_code=status.HTTP_200_OK)
def logout(response: Response) -> AuthSessionResponse:
    clear_auth_cookies(response, get_settings())
    return _session_response(None)


def _session_response(owner_session: OwnerSession | None) -> AuthSessionResponse:
    return AuthSessionResponse(
        auth_enabled=True,
        authenticated=owner_session is not None,
        can_write=owner_session is not None,
        username=owner_session.username if owner_session else None,
    )
