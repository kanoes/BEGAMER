from collections.abc import Iterable
from datetime import UTC, datetime

from begamer_worker.models import AccountRecord, GameRecord
from begamer_worker.schemas import (
    AccountRead,
    CollectionSuggestion,
    DashboardResponse,
    DashboardStats,
    GameListResponse,
    GameRead,
    GameShelf,
    GameStatus,
)


def classify_game(game: GameRecord) -> GameStatus:
    if game.playtime_forever == 0:
        return GameStatus.UNPLAYED
    if game.playtime_2weeks > 0:
        return GameStatus.RECENT
    if game.playtime_forever >= 6_000:
        return GameStatus.DEEP
    return GameStatus.BACKLOG


def game_read(game: GameRecord) -> GameRead:
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


def account_read(account: AccountRecord) -> AccountRead:
    return AccountRead(
        steam_id=account.steam_id,
        display_name=account.display_name,
        profile_url=account.profile_url,
        avatar_url=account.avatar_url,
        is_demo=account.is_demo,
        last_synced_at=account.last_synced_at,
    )


def sorted_games(games: Iterable[GameRecord], sort: str) -> list[GameRecord]:
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


def game_list(
    games: list[GameRecord],
    *,
    query: str | None,
    status: GameStatus | None,
    favorite: bool | None,
    sort: str,
    page: int,
    page_size: int,
) -> GameListResponse:
    filtered: Iterable[GameRecord] = games
    if query:
        normalized = query.casefold().strip()
        filtered = [game for game in filtered if normalized in game.name.casefold()]
    if status:
        filtered = [game for game in filtered if classify_game(game) == status]
    if favorite is not None:
        filtered = [game for game in filtered if game.favorite is favorite]

    ordered = sorted_games(filtered, sort)
    total = len(ordered)
    start = (page - 1) * page_size
    return GameListResponse(
        items=[game_read(game) for game in ordered[start : start + page_size]],
        total=total,
        page=page,
        page_size=page_size,
    )


def dashboard(account: AccountRecord, games: list[GameRecord]) -> DashboardResponse:
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


def suggest_collections(games: list[GameRecord]) -> list[CollectionSuggestion]:
    definitions = [
        (
            "in-motion",
            "ACTIVE SIGNAL",
            "正在发生",
            "最近两周仍然有游玩记录，适合保持手感。",
            "lime",
            [game for game in games if classify_game(game) == GameStatus.RECENT],
            "recent",
        ),
        (
            "first-contact",
            "ZERO HOUR",
            "第一次见面",
            "已经拥有，但总游玩时间仍是零分钟。",
            "violet",
            [game for game in games if classify_game(game) == GameStatus.UNPLAYED],
            "added",
        ),
        (
            "deep-orbit",
            "100H CLUB",
            "长期轨道",
            "投入超过 100 小时，已经成为习惯的一部分。",
            "blue",
            [game for game in games if classify_game(game) == GameStatus.DEEP],
            "playtime",
        ),
        (
            "second-chance",
            "REDISCOVER",
            "再给一次机会",
            "玩过一些、最近却没有打开，适合重新评估。",
            "amber",
            [
                game
                for game in games
                if classify_game(game) == GameStatus.BACKLOG and game.playtime_forever <= 1_200
            ],
            "recent",
        ),
    ]
    return [
        CollectionSuggestion(
            id=identifier,
            eyebrow=eyebrow,
            title=title,
            description=description,
            accent=accent,
            games=[game_read(game) for game in sorted_games(members, sort)[:6]],
            total=len(members),
        )
        for identifier, eyebrow, title, description, accent, members, sort in definitions
    ]
