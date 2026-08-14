from begamer.db.models import LibraryEntry
from begamer.schemas import CollectionSuggestion, GameStatus
from begamer.services.library import classify_game, game_read, sorted_games


def suggest_collections(games: list[LibraryEntry]) -> list[CollectionSuggestion]:
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

    suggestions: list[CollectionSuggestion] = []
    for identifier, eyebrow, title, description, accent, members, sort in definitions:
        ordered = sorted_games(members, sort)
        suggestions.append(
            CollectionSuggestion(
                id=identifier,
                eyebrow=eyebrow,
                title=title,
                description=description,
                accent=accent,
                games=[game_read(game) for game in ordered[:6]],
                total=len(ordered),
            )
        )
    return suggestions
