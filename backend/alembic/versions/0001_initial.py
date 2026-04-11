"""initial schema

Revision ID: 0001_initial
Revises: None
Create Date: 2026-04-10 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


anime_status = postgresql.ENUM("unwatched", "watching", "completed", name="anime_status", create_type=False)
anime_season = postgresql.ENUM("winter", "spring", "summer", "fall", "other", name="anime_season", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    anime_status.create(bind, checkfirst=True)
    anime_season.create(bind, checkfirst=True)

    op.create_table(
        "anime",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("name_normalized", sa.Text(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("season", anime_season, nullable=False),
        sa.Column("status", anime_status, nullable=False, server_default="unwatched"),
        sa.Column("type", sa.Text(), nullable=False, server_default=""),
        sa.Column("comment", sa.Text(), nullable=False, server_default=""),
        sa.Column("url", sa.Text(), nullable=False, server_default=""),
        sa.Column("downloaded", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("year BETWEEN 1960 AND 2100", name="year_range"),
        sa.CheckConstraint("char_length(name) BETWEEN 1 AND 255", name="name_length"),
        sa.CheckConstraint("char_length(url) <= 2048", name="url_length"),
    )
    op.create_index("ix_anime_year_season_name_norm", "anime", ["year", "season", "name_normalized"], unique=False)
    op.create_index("ix_anime_status", "anime", ["status"], unique=False)
    op.create_index("ix_anime_downloaded", "anime", ["downloaded"], unique=False)
    op.create_index("uq_anime_name_norm_year_season", "anime", ["name_normalized", "year", "season"], unique=True)

    op.create_table(
        "shikimori_cache",
        sa.Column("search_key", sa.Text(), primary_key=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_shikimori_cache_expires_at", "shikimori_cache", ["expires_at"], unique=False)

    op.create_table(
        "year_scaffold",
        sa.Column("year", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "app_preferences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("last_scope_kind", sa.Text(), nullable=False, server_default="year"),
        sa.Column("last_scope_year", sa.Integer(), nullable=True),
        sa.Column("last_used_season", anime_season, nullable=True),
        sa.Column("density", sa.Text(), nullable=False, server_default="comfortable"),
        sa.Column("theme", sa.Text(), nullable=False, server_default="system"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade() -> None:
    op.drop_table("app_preferences")
    op.drop_table("year_scaffold")
    op.drop_index("ix_shikimori_cache_expires_at", table_name="shikimori_cache")
    op.drop_table("shikimori_cache")
    op.drop_index("uq_anime_name_norm_year_season", table_name="anime")
    op.drop_index("ix_anime_downloaded", table_name="anime")
    op.drop_index("ix_anime_status", table_name="anime")
    op.drop_index("ix_anime_year_season_name_norm", table_name="anime")
    op.drop_table("anime")

    bind = op.get_bind()
    anime_status.drop(bind, checkfirst=True)
    anime_season.drop(bind, checkfirst=True)
