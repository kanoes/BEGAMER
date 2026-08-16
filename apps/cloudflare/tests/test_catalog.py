from datetime import UTC, datetime

from begamer_worker.catalog import classify_game, game_list
from begamer_worker.models import GameRecord
from begamer_worker.recommendations import local_recommendation
from begamer_worker.schemas import GameStatus, RecommendationRequest

NOW = datetime(2026, 8, 16, tzinfo=UTC)


def game(
    app_id: int,
    name: str,
    *,
    minutes: int = 0,
    recent: int = 0,
    favorite: bool = False,
    moods: list[str] | None = None,
) -> GameRecord:
    return GameRecord(
        account_id=1,
        app_id=app_id,
        name=name,
        cover_url=f"https://example.com/{app_id}/cover.jpg",
        hero_url=f"https://example.com/{app_id}/hero.jpg",
        playtime_forever=minutes,
        playtime_2weeks=recent,
        favorite=favorite,
        moods=moods or [],
        first_seen_at=NOW,
        last_seen_at=NOW,
        updated_at=NOW,
    )


def test_catalog_classification_and_filtering() -> None:
    unplayed = game(1, "Unplayed")
    recent = game(2, "Recent", minutes=600, recent=60)
    deep = game(3, "Deep", minutes=6_001, favorite=True)

    assert classify_game(unplayed) == GameStatus.UNPLAYED
    assert classify_game(recent) == GameStatus.RECENT
    assert classify_game(deep) == GameStatus.DEEP

    result = game_list(
        [unplayed, recent, deep],
        query=None,
        status=None,
        favorite=True,
        sort="playtime",
        page=1,
        page_size=48,
    )
    assert result.total == 1
    assert result.items[0].app_id == deep.app_id


def test_recommendation_honors_unplayed_preference() -> None:
    games = [
        game(1, "Familiar", minutes=400, favorite=True),
        game(2, "Fresh Start", moods=["轻松"]),
    ]

    result = local_recommendation(
        games,
        RecommendationRequest(prompt="想玩一个没玩过的轻松游戏", prefer_unplayed=True),
    )

    assert [pick.game.app_id for pick in result.picks] == [2]
    assert result.generation_mode == "deterministic"
