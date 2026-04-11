from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON, Boolean, DateTime, Enum, Index, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def enum_values(enum_cls: type[StrEnum]) -> list[str]:
    return [member.value for member in enum_cls]


class AnimeStatus(StrEnum):
    UNWATCHED = "unwatched"
    WATCHING = "watching"
    COMPLETED = "completed"


class AnimeSeason(StrEnum):
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    OTHER = "other"


class Anime(Base):
    __tablename__ = "anime"
    __table_args__ = (
        Index("ix_anime_year_season_name_norm", "year", "season", "name_normalized"),
        Index("ix_anime_status", "status"),
        Index("ix_anime_downloaded", "downloaded"),
        Index("uq_anime_name_norm_year_season", "name_normalized", "year", "season", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    name_normalized: Mapped[str] = mapped_column(Text, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    season: Mapped[AnimeSeason] = mapped_column(
        Enum(AnimeSeason, name="anime_season", native_enum=True, values_callable=enum_values),
        nullable=False,
        default=AnimeSeason.OTHER,
    )
    status: Mapped[AnimeStatus] = mapped_column(
        Enum(AnimeStatus, name="anime_status", native_enum=True, values_callable=enum_values),
        nullable=False,
        default=AnimeStatus.UNWATCHED,
    )
    type: Mapped[str] = mapped_column(Text, nullable=False, default="")
    comment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    downloaded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ShikimoriCache(Base):
    __tablename__ = "shikimori_cache"
    __table_args__ = (Index("ix_shikimori_cache_expires_at", "expires_at"),)

    search_key: Mapped[str] = mapped_column(Text, primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class YearScaffold(Base):
    __tablename__ = "year_scaffold"

    year: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class AppPreferences(Base):
    __tablename__ = "app_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    last_scope_kind: Mapped[str] = mapped_column(Text, nullable=False, default="year")
    last_scope_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_used_season: Mapped[AnimeSeason | None] = mapped_column(
        Enum(AnimeSeason, name="anime_season", native_enum=True, values_callable=enum_values),
        nullable=True,
    )
    density: Mapped[str] = mapped_column(Text, nullable=False, default="comfortable")
    theme: Mapped[str] = mapped_column(Text, nullable=False, default="system")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
