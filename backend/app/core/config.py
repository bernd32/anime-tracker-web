from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, AliasChoices, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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

    cors_allow_origins: list[str] = ["http://localhost:20773", "http://127.0.0.1:20773"]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
