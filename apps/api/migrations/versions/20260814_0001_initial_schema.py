"""Create Steam accounts and local library entries.

Revision ID: 20260814_0001
Revises:
Create Date: 2026-08-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260814_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "steam_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("steam_id", sa.String(length=32), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("profile_url", sa.String(length=500), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("is_demo", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_steam_accounts_is_active", "steam_accounts", ["is_active"])
    op.create_index(
        "ix_steam_accounts_steam_id",
        "steam_accounts",
        ["steam_id"],
        unique=True,
    )

    op.create_table(
        "library_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("app_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=240), nullable=False),
        sa.Column("icon_url", sa.String(length=500), nullable=True),
        sa.Column("cover_url", sa.String(length=500), nullable=False),
        sa.Column("hero_url", sa.String(length=500), nullable=False),
        sa.Column("playtime_forever", sa.Integer(), nullable=False),
        sa.Column("playtime_2weeks", sa.Integer(), nullable=False),
        sa.Column("last_played_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("achievements_unlocked", sa.Integer(), nullable=True),
        sa.Column("achievements_total", sa.Integer(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("moods", sa.JSON(), nullable=False),
        sa.Column("favorite", sa.Boolean(), nullable=False),
        sa.Column("custom_status", sa.String(length=40), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["steam_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id", "app_id", name="uq_library_account_app"),
    )
    op.create_index("ix_library_entries_app_id", "library_entries", ["app_id"])
    op.create_index("ix_library_entries_name", "library_entries", ["name"])


def downgrade() -> None:
    op.drop_index("ix_library_entries_name", table_name="library_entries")
    op.drop_index("ix_library_entries_app_id", table_name="library_entries")
    op.drop_table("library_entries")
    op.drop_index("ix_steam_accounts_steam_id", table_name="steam_accounts")
    op.drop_index("ix_steam_accounts_is_active", table_name="steam_accounts")
    op.drop_table("steam_accounts")
