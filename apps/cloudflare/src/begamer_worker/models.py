from datetime import datetime

from pydantic import BaseModel, Field


class AccountRecord(BaseModel):
    id: int
    user_id: str
    steam_id: str
    display_name: str
    profile_url: str | None = None
    avatar_url: str | None = None
    is_demo: bool = False
    is_active: bool = True
    last_synced_at: datetime | None = None
    created_at: datetime


class GameRecord(BaseModel):
    id: int | None = None
    account_id: int
    app_id: int
    name: str
    icon_url: str | None = None
    cover_url: str
    hero_url: str
    playtime_forever: int = 0
    playtime_2weeks: int = 0
    last_played_at: datetime | None = None
    achievements_unlocked: int | None = None
    achievements_total: int | None = None
    tags: list[str] = Field(default_factory=list)
    moods: list[str] = Field(default_factory=list)
    favorite: bool = False
    custom_status: str | None = None
    note: str | None = None
    first_seen_at: datetime
    last_seen_at: datetime
    updated_at: datetime
