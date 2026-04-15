from app.schemas.common import APIModel


class LoginRequest(APIModel):
    username: str
    password: str


class AuthSessionResponse(APIModel):
    auth_enabled: bool
    authenticated: bool
    can_write: bool
    username: str | None = None
