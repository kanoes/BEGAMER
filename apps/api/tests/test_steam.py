from pathlib import Path

import httpx
import pytest
from sqlalchemy import func, select

from begamer.clients.steam import SteamClient, SteamClientError
from begamer.core.config import Settings
from begamer.db.models import LibraryEntry, SteamAccount
from begamer.db.session import Database
from begamer.services.steam_sync import sync_steam_library


def steam_transport(request: httpx.Request) -> httpx.Response:
    assert request.headers["x-webapi-key"] == "test-secret"
    assert "test-secret" not in str(request.url)

    if request.url.path.endswith("GetOwnedGames/v1/"):
        return httpx.Response(
            200,
            json={
                "response": {
                    "game_count": 2,
                    "games": [
                        {
                            "appid": 10,
                            "name": "Counter-Strike",
                            "playtime_forever": 120,
                            "img_icon_url": "iconhash",
                        },
                        {"appid": 20, "name": "Team Fortress Classic", "playtime_forever": 0},
                    ],
                }
            },
        )
    if request.url.path.endswith("GetRecentlyPlayedGames/v1/"):
        return httpx.Response(
            200,
            json={
                "response": {
                    "total_count": 1,
                    "games": [
                        {
                            "appid": 10,
                            "name": "Counter-Strike",
                            "playtime_forever": 120,
                            "playtime_2weeks": 30,
                            "rtime_last_played": 1_700_000_000,
                        }
                    ],
                }
            },
        )
    if request.url.path.endswith("GetPlayerSummaries/v2/"):
        return httpx.Response(
            200,
            json={
                "response": {
                    "players": [
                        {
                            "steamid": "76561198000000000",
                            "personaname": "Test Player",
                            "profileurl": "https://steamcommunity.com/profiles/76561198000000000",
                        }
                    ]
                }
            },
        )
    return httpx.Response(404)


@pytest.mark.asyncio
async def test_steam_sync_is_idempotent_and_keeps_key_out_of_url(tmp_path: Path) -> None:
    database = Database(f"sqlite+aiosqlite:///{tmp_path / 'steam-sync.db'}")
    await database.create_all()
    transport = httpx.MockTransport(steam_transport)
    async with httpx.AsyncClient(transport=transport) as http_client:
        steam = SteamClient(api_key="test-secret", client=http_client)
        settings = Settings(
            database_url=database.url,
            steam_web_api_key="test-secret",
            seed_demo_data=False,
        )
        async with database.sessions() as session:
            first = await sync_steam_library(
                session,
                settings=settings,
                steam_id="76561198000000000",
                client=steam,
            )
            second = await sync_steam_library(
                session,
                settings=settings,
                steam_id="76561198000000000",
                client=steam,
            )
            count = await session.scalar(select(func.count()).select_from(LibraryEntry))
            account = await session.scalar(
                select(SteamAccount).where(SteamAccount.steam_id == "76561198000000000")
            )

    await database.dispose()
    assert first.seen_games == 2
    assert second.seen_games == 2
    assert count == 2
    assert account is not None
    assert account.display_name == "Test Player"


@pytest.mark.asyncio
async def test_missing_game_count_is_treated_as_private_not_empty() -> None:
    transport = httpx.MockTransport(lambda _request: httpx.Response(200, json={"response": {}}))
    async with httpx.AsyncClient(transport=transport) as http_client:
        steam = SteamClient(api_key="test-secret", client=http_client)
        with pytest.raises(SteamClientError) as error:
            await steam.get_library("76561198000000000")

    assert error.value.code == "STEAM_GAME_DETAILS_PRIVATE_OR_UNAVAILABLE"
