from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from begamer.clients.steam import (
    SteamClient,
    steam_cover_url,
    steam_hero_url,
    steam_icon_url,
    steam_timestamp,
)
from begamer.core.config import Settings
from begamer.db.models import LibraryEntry, SteamAccount
from begamer.schemas import SyncResponse
from begamer.services.library import account_read


async def sync_steam_library(
    session: AsyncSession,
    *,
    settings: Settings,
    steam_id: str,
    client: SteamClient | None = None,
) -> SyncResponse:
    if not settings.steam_web_api_key and client is None:
        raise ValueError("请先在 .env 中配置 STEAM_WEB_API_KEY。")

    steam = client or SteamClient(
        api_key=settings.steam_web_api_key or "",
        base_url=settings.steam_api_base_url,
    )
    library = await steam.get_library(steam_id)
    now = datetime.now(UTC)

    account = await session.scalar(
        select(SteamAccount).where(SteamAccount.steam_id == library.profile.steamid)
    )
    if account is None:
        account = SteamAccount(
            steam_id=library.profile.steamid,
            display_name=library.profile.personaname,
            is_active=True,
            is_demo=False,
        )
        session.add(account)
        await session.flush()

    await session.execute(
        update(SteamAccount).where(SteamAccount.id != account.id).values(is_active=False)
    )
    account.display_name = library.profile.personaname
    account.profile_url = library.profile.profileurl
    account.avatar_url = library.profile.avatarfull
    account.is_active = True
    account.last_synced_at = now

    existing_result = await session.scalars(
        select(LibraryEntry).where(LibraryEntry.account_id == account.id)
    )
    existing = {entry.app_id: entry for entry in existing_result.all()}

    updated = 0
    for steam_game in library.games:
        entry = existing.get(steam_game.appid)
        if entry is None:
            entry = LibraryEntry(
                account_id=account.id,
                app_id=steam_game.appid,
                name=steam_game.name,
                cover_url=steam_cover_url(steam_game.appid),
                hero_url=steam_hero_url(steam_game.appid),
                first_seen_at=now,
                tags=[],
                moods=[],
            )
            session.add(entry)
        entry.name = steam_game.name
        entry.icon_url = steam_icon_url(steam_game.appid, steam_game.img_icon_url)
        entry.playtime_forever = steam_game.playtime_forever
        entry.playtime_2weeks = steam_game.playtime_2weeks
        entry.last_played_at = steam_timestamp(steam_game.rtime_last_played)
        entry.last_seen_at = now
        updated += 1

    await session.commit()
    return SyncResponse(
        account=account_read(account),
        seen_games=len(library.games),
        updated_games=updated,
        message=f"已同步 {len(library.games)} 款游戏。现有本地标记已保留。",
    )
