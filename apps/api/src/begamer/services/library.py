from collections.abc import Iterable
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from begamer.db.models import LibraryEntry, SteamAccount
from begamer.schemas import (
    AccountRead,
    DashboardResponse,
    DashboardStats,
    GameListResponse,
    GameRead,
    GameShelf,
    GameStatus,
    GameUpdate,
)


class LibraryNotFoundError(RuntimeError):
    pass


async def get_active_account(session: AsyncSession) -> SteamAccount:
    account = await session.scalar(
        select(SteamAccount).where(SteamAccount.is_active.is_(True)).limit(1)
    )
    if account is None:
        raise LibraryNotFoundError("还没有可用的游戏库。")
    return account


def classify_game(game: LibraryEntry) -> GameStatus:
    if game.playtime_forever == 0:
        return GameStatus.UNPLAYED
    if game.playtime_2weeks > 0:
        return GameStatus.RECENT
    if game.playtime_forever >= 6_000:
        return GameStatus.DEEP
    return GameStatus.BACKLOG


def game_read(game: LibraryEntry) -> GameRead:
    return GameRead(
        app_id=game.app_id,
        name=game.name,
        icon_url=game.icon_url,
        cover_url=game.cover_url,
        hero_url=game.hero_url,
        playtime_forever=game.playtime_forever,
        playtime_2weeks=game.playtime_2weeks,
        last_played_at=game.last_played_at,
        achievements_unlocked=game.achievements_unlocked,
        achievements_total=game.achievements_total,
        tags=game.tags,
        moods=game.moods,
        favorite=game.favorite,
        custom_status=game.custom_status,
        note=game.note,
        status=classify_game(game),
    )


def account_read(account: SteamAccount) -> AccountRead:
    return AccountRead.model_validate(account)


def sorted_games(games: Iterable[LibraryEntry], sort: str) -> list[LibraryEntry]:
    if sort == "name":
        return sorted(games, key=lambda game: game.name.casefold())
    if sort == "recent":
        return sorted(
            games,
            key=lambda game: game.last_played_at or datetime.min.replace(tzinfo=UTC),
            reverse=True,
        )
    if sort == "added":
        return sorted(games, key=lambda game: game.first_seen_at, reverse=True)
    return sorted(games, key=lambda game: (-game.playtime_forever, game.name.casefold()))


async def list_games(
    session: AsyncSession,
    *,
    query: str | None,
    status: GameStatus | None,
    favorite: bool | None,
    sort: str,
    page: int,
    page_size: int,
) -> GameListResponse:
    account = await get_active_account(session)
    games: Iterable[LibraryEntry] = account.library

    if query:
        normalized = query.casefold().strip()
        games = [game for game in games if normalized in game.name.casefold()]
    if status:
        games = [game for game in games if classify_game(game) == status]
    if favorite is not None:
        games = [game for game in games if game.favorite is favorite]

    ordered = sorted_games(games, sort)
    total = len(ordered)
    start = (page - 1) * page_size
    return GameListResponse(
        items=[game_read(game) for game in ordered[start : start + page_size]],
        total=total,
        page=page,
        page_size=page_size,
    )


async def update_game(
    session: AsyncSession,
    *,
    app_id: int,
    update: GameUpdate,
) -> GameRead:
    account = await get_active_account(session)
    game = next((item for item in account.library if item.app_id == app_id), None)
    if game is None:
        raise LibraryNotFoundError("游戏不在当前库中。")

    fields = update.model_fields_set
    if "favorite" in fields:
        game.favorite = bool(update.favorite)
    if "custom_status" in fields:
        game.custom_status = update.custom_status or None
    if "note" in fields:
        game.note = update.note or None
    await session.commit()
    return game_read(game)


async def dashboard(session: AsyncSession) -> DashboardResponse:
    account = await get_active_account(session)
    games = list(account.library)
    recent = sorted_games(
        (game for game in games if classify_game(game) == GameStatus.RECENT),
        "recent",
    )
    unplayed = sorted_games(
        (game for game in games if classify_game(game) == GameStatus.UNPLAYED),
        "added",
    )
    deep = sorted_games(
        (game for game in games if classify_game(game) == GameStatus.DEEP),
        "playtime",
    )
    rediscover = sorted_games(
        (
            game
            for game in games
            if classify_game(game) == GameStatus.BACKLOG and game.playtime_forever > 120
        ),
        "recent",
    )
    spotlight = (
        recent[0] if recent else (unplayed[0] if unplayed else (games[0] if games else None))
    )

    return DashboardResponse(
        account=account_read(account),
        stats=DashboardStats(
            total_games=len(games),
            total_hours=round(sum(game.playtime_forever for game in games) / 60, 1),
            unplayed_games=len(unplayed),
            recent_games=len(recent),
            deep_games=len(deep),
        ),
        spotlight=game_read(spotlight) if spotlight else None,
        shelves=[
            GameShelf(
                id="continue",
                title="继续上次的旅程",
                description="最近两周仍在玩的游戏",
                games=[game_read(game) for game in recent[:8]],
            ),
            GameShelf(
                id="unplayed",
                title="等待第一次启动",
                description="买下之后，还没真正见过的世界",
                games=[game_read(game) for game in unplayed[:8]],
            ),
            GameShelf(
                id="rediscover",
                title="值得重新捡起来",
                description="曾经开始，但最近没有继续",
                games=[game_read(game) for game in rediscover[:8]],
            ),
        ],
    )
