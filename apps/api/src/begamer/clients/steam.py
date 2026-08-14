import asyncio
from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field


class SteamClientError(RuntimeError):
    def __init__(self, code: str, message: str, *, status_code: int = 502) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class SteamGame(BaseModel):
    model_config = ConfigDict(extra="ignore")

    appid: int
    name: str
    img_icon_url: str | None = None
    playtime_forever: int = 0
    playtime_2weeks: int = 0
    rtime_last_played: int | None = None


class SteamProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    steamid: str
    personaname: str = "Steam Player"
    profileurl: str | None = None
    avatarfull: str | None = None
    communityvisibilitystate: int | None = None


class SteamLibrary(BaseModel):
    profile: SteamProfile
    games: list[SteamGame]
    game_count: int = Field(ge=0)


class SteamClient:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.steampowered.com",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._external_client = client

    async def get_library(self, steam_id: str) -> SteamLibrary:
        owned = await self._get(
            "/IPlayerService/GetOwnedGames/v1/",
            {
                "steamid": steam_id,
                "include_appinfo": "true",
                "include_played_free_games": "true",
            },
        )
        response = owned.get("response")
        if not isinstance(response, dict) or "game_count" not in response:
            raise SteamClientError(
                "STEAM_GAME_DETAILS_PRIVATE_OR_UNAVAILABLE",
                "Steam 没有返回游戏数量。请确认“游戏详情”隐私设置已公开。",
                status_code=409,
            )

        raw_games = response.get("games", [])
        if not isinstance(raw_games, list):
            raw_games = []
        games = [SteamGame.model_validate(game) for game in raw_games]

        recent_by_app = await self._recent_games(steam_id)
        for game in games:
            recent = recent_by_app.get(game.appid)
            if recent is not None:
                game.playtime_2weeks = recent.playtime_2weeks
                game.rtime_last_played = recent.rtime_last_played

        profile = await self._profile(steam_id)
        return SteamLibrary(profile=profile, games=games, game_count=int(response["game_count"]))

    async def _recent_games(self, steam_id: str) -> dict[int, SteamGame]:
        try:
            payload = await self._get(
                "/IPlayerService/GetRecentlyPlayedGames/v1/",
                {"steamid": steam_id, "count": "0"},
            )
        except SteamClientError:
            return {}

        response = payload.get("response")
        if not isinstance(response, dict):
            return {}
        games = response.get("games", [])
        if not isinstance(games, list):
            return {}
        parsed = [SteamGame.model_validate(game) for game in games]
        return {game.appid: game for game in parsed}

    async def _profile(self, steam_id: str) -> SteamProfile:
        try:
            payload = await self._get(
                "/ISteamUser/GetPlayerSummaries/v2/",
                {"steamids": steam_id},
            )
            response = payload.get("response")
            players = response.get("players", []) if isinstance(response, dict) else []
            if isinstance(players, list) and players:
                return SteamProfile.model_validate(players[0])
        except SteamClientError:
            pass
        return SteamProfile(steamid=steam_id)

    async def _get(self, path: str, params: dict[str, str]) -> dict[str, Any]:
        owns_client = self._external_client is None
        client = self._external_client or httpx.AsyncClient(timeout=15.0)
        try:
            for attempt in range(3):
                try:
                    response = await client.get(
                        f"{self.base_url}{path}",
                        params=params,
                        headers={"x-webapi-key": self.api_key},
                    )
                except httpx.RequestError as error:
                    if attempt == 2:
                        raise SteamClientError(
                            "STEAM_NETWORK_ERROR",
                            "暂时无法连接 Steam，请稍后重试。",
                        ) from error
                    await asyncio.sleep(0.15 * (2**attempt))
                    continue

                if response.status_code in {401, 403}:
                    raise SteamClientError(
                        "STEAM_API_KEY_INVALID",
                        "Steam API Key 无效或无权访问该接口。",
                        status_code=409,
                    )
                if (response.status_code == 429 or response.status_code >= 500) and attempt < 2:
                    await asyncio.sleep(0.15 * (2**attempt))
                    continue
                try:
                    response.raise_for_status()
                    payload = response.json()
                except (httpx.HTTPStatusError, ValueError) as error:
                    raise SteamClientError(
                        "STEAM_UPSTREAM_ERROR",
                        "Steam 返回了无法处理的响应。",
                    ) from error
                if not isinstance(payload, dict):
                    raise SteamClientError(
                        "STEAM_UPSTREAM_ERROR",
                        "Steam 返回了无法处理的数据格式。",
                    )
                return payload
        finally:
            if owns_client:
                await client.aclose()

        raise SteamClientError("STEAM_UPSTREAM_ERROR", "Steam 请求失败。")


def steam_timestamp(value: int | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromtimestamp(value, tz=UTC)


def steam_icon_url(app_id: int, icon_hash: str | None) -> str | None:
    if not icon_hash:
        return None
    return (
        f"https://media.steampowered.com/steamcommunity/public/images/apps/{app_id}/{icon_hash}.jpg"
    )


def steam_cover_url(app_id: int) -> str:
    return f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{app_id}/library_600x900.jpg"


def steam_hero_url(app_id: int) -> str:
    return f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{app_id}/library_hero.jpg"
