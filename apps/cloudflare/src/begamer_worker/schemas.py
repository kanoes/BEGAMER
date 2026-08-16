from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class GameStatus(StrEnum):
    UNPLAYED = "unplayed"
    RECENT = "recent"
    DEEP = "deep"
    BACKLOG = "backlog"


class SessionUser(BaseModel):
    sub: str
    email: str
    display_name: str
    avatar_url: str | None = None


class AuthConfig(BaseModel):
    auth_required: bool
    google_client_id: str | None


class GoogleCredential(BaseModel):
    credential: str = Field(min_length=20, max_length=10_000)


class AccountRead(BaseModel):
    steam_id: str
    display_name: str
    profile_url: str | None
    avatar_url: str | None
    is_demo: bool
    last_synced_at: datetime | None


class GameRead(BaseModel):
    app_id: int
    name: str
    icon_url: str | None
    cover_url: str
    hero_url: str
    playtime_forever: int
    playtime_2weeks: int
    last_played_at: datetime | None
    achievements_unlocked: int | None
    achievements_total: int | None
    tags: list[str]
    moods: list[str]
    favorite: bool
    custom_status: str | None
    note: str | None
    status: GameStatus


class GameListResponse(BaseModel):
    items: list[GameRead]
    total: int
    page: int
    page_size: int


class GameUpdate(BaseModel):
    favorite: bool | None = None
    custom_status: str | None = Field(default=None, max_length=40)
    note: str | None = Field(default=None, max_length=1000)


class DashboardStats(BaseModel):
    total_games: int
    total_hours: float
    unplayed_games: int
    recent_games: int
    deep_games: int


class GameShelf(BaseModel):
    id: str
    title: str
    description: str
    games: list[GameRead]


class DashboardResponse(BaseModel):
    account: AccountRead
    stats: DashboardStats
    spotlight: GameRead | None
    shelves: list[GameShelf]


class CollectionSuggestion(BaseModel):
    id: str
    eyebrow: str
    title: str
    description: str
    accent: str
    games: list[GameRead]
    total: int


class RecommendationRequest(BaseModel):
    prompt: str = Field(min_length=2, max_length=500)
    max_results: int = Field(default=3, ge=1, le=6)
    prefer_unplayed: bool = False


class RecommendationPick(BaseModel):
    game: GameRead
    reason: str
    fit_score: int = Field(ge=0, le=100)


class RecommendationResponse(BaseModel):
    headline: str
    summary: str
    picks: list[RecommendationPick]
    generation_mode: str
    model: str | None = None
    fallback_reason: str | None = None


class SyncRequest(BaseModel):
    steam_id: str | None = Field(default=None, min_length=17, max_length=20)


class SyncResponse(BaseModel):
    account: AccountRead
    seen_games: int
    updated_games: int
    message: str


class CapabilityResponse(BaseModel):
    steam_configured: bool
    llm_configured: bool
    llm_model: str
    active_source: str
    steam_write_supported: bool = False


class HealthResponse(BaseModel):
    status: str
    version: str
