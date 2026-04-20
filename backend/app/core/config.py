from functools import lru_cache
from typing import ClassVar, Literal

from pydantic import AnyHttpUrl, AliasChoices, Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEFAULT_AUTH_OWNER_USERNAME: ClassVar[str] = "owner"
    DEFAULT_AUTH_OWNER_PASSWORD: ClassVar[str] = "change-this-dev-password"
    DEFAULT_AUTH_SESSION_SECRET: ClassVar[str] = "change-this-dev-session-secret-at-least-32-bytes"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Anime Backlog API"
    app_env: Literal["development", "test", "production"] = "development"
    app_debug: bool = False
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    auth_owner_username: str = Field(
        default=DEFAULT_AUTH_OWNER_USERNAME,
        validation_alias=AliasChoices("AUTH_OWNER_USERNAME", "auth_owner_username"),
    )
    auth_owner_password: str = Field(
        default=DEFAULT_AUTH_OWNER_PASSWORD,
        validation_alias=AliasChoices("AUTH_OWNER_PASSWORD", "auth_owner_password"),
    )
    auth_session_secret: str = Field(
        default=DEFAULT_AUTH_SESSION_SECRET,
        validation_alias=AliasChoices("AUTH_SESSION_SECRET", "auth_session_secret"),
    )
    auth_session_max_age_seconds: int = Field(
        default=60 * 60 * 24 * 30,
        validation_alias=AliasChoices("AUTH_SESSION_MAX_AGE_SECONDS", "auth_session_max_age_seconds"),
    )
    auth_login_max_failures: int = Field(
        default=5,
        validation_alias=AliasChoices("AUTH_LOGIN_MAX_FAILURES", "auth_login_max_failures"),
    )
    auth_login_window_seconds: int = Field(
        default=60 * 10,
        validation_alias=AliasChoices("AUTH_LOGIN_WINDOW_SECONDS", "auth_login_window_seconds"),
    )
    auth_login_lockout_seconds: int = Field(
        default=60 * 15,
        validation_alias=AliasChoices("AUTH_LOGIN_LOCKOUT_SECONDS", "auth_login_lockout_seconds"),
    )

    database_url: str = Field(
        default="sqlite+pysqlite:///./anime_backlog.db",
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
    )

    shikimori_graphql_url: AnyHttpUrl = Field(
        default="https://shikimori.one/api/graphql",
        validation_alias=AliasChoices("SHIKIMORI_GRAPHQL_URL", "shikimori_graphql_url"),
    )
    shikimori_request_timeout_seconds: float = 10.0
    shikimori_cache_ttl_seconds: int = 365 * 24 * 60 * 60
    shikimori_user_agent: str = "anime-backlog-web/1.0"
    shikimori_https_proxy_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SHIKIMORI_HTTPS_PROXY_URL", "shikimori_https_proxy_url"),
    )
    shikimori_socks5_proxy_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SHIKIMORI_SOCKS5_PROXY_URL", "shikimori_socks5_proxy_url"),
    )

    cors_allow_origins: list[str] = ["http://localhost:20773", "http://127.0.0.1:20773"]

    @model_validator(mode="after")
    def validate_shikimori_proxy_settings(self) -> "Settings":
        if self.shikimori_https_proxy_url and self.shikimori_socks5_proxy_url:
            raise ValueError(
                "Set only one of SHIKIMORI_HTTPS_PROXY_URL or SHIKIMORI_SOCKS5_PROXY_URL."
            )

        if self.shikimori_https_proxy_url and not self.shikimori_https_proxy_url.startswith(
            ("http://", "https://")
        ):
            raise ValueError(
                "SHIKIMORI_HTTPS_PROXY_URL must start with http:// or https://."
            )

        if self.shikimori_socks5_proxy_url and not self.shikimori_socks5_proxy_url.startswith(
            ("socks5://", "socks5h://")
        ):
            raise ValueError(
                "SHIKIMORI_SOCKS5_PROXY_URL must start with socks5:// or socks5h://."
            )

        return self

    @model_validator(mode="after")
    def validate_auth_settings(self) -> "Settings":
        if len(self.auth_owner_username.strip()) < 3:
            raise ValueError("AUTH_OWNER_USERNAME must be at least 3 characters long.")
        if len(self.auth_owner_password) < 12:
            raise ValueError("AUTH_OWNER_PASSWORD must be at least 12 characters long.")
        if len(self.auth_session_secret) < 32:
            raise ValueError("AUTH_SESSION_SECRET must be at least 32 characters long.")
        if self.auth_login_max_failures < 1:
            raise ValueError("AUTH_LOGIN_MAX_FAILURES must be at least 1.")
        if self.auth_login_window_seconds < 1:
            raise ValueError("AUTH_LOGIN_WINDOW_SECONDS must be at least 1.")
        if self.auth_login_lockout_seconds < 1:
            raise ValueError("AUTH_LOGIN_LOCKOUT_SECONDS must be at least 1.")

        uses_insecure_defaults = (
            self.auth_owner_username == self.DEFAULT_AUTH_OWNER_USERNAME
            or self.auth_owner_password == self.DEFAULT_AUTH_OWNER_PASSWORD
            or self.auth_session_secret == self.DEFAULT_AUTH_SESSION_SECRET
        )
        if self.app_env == "production" and uses_insecure_defaults:
            raise ValueError(
                "Configure AUTH_OWNER_USERNAME, AUTH_OWNER_PASSWORD, and AUTH_SESSION_SECRET "
                "before starting the app in production."
            )
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def shikimori_proxy_url(self) -> str | None:
        return self.shikimori_socks5_proxy_url or self.shikimori_https_proxy_url

    @computed_field  # type: ignore[prop-decorator]
    @property
    def auth_cookie_secure(self) -> bool:
        return self.app_env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
