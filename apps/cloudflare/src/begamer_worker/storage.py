import json
from datetime import UTC, datetime, timedelta
from typing import Any

from begamer_worker.models import AccountRecord, GameRecord
from begamer_worker.schemas import GameUpdate, SessionUser
from begamer_worker.seed import DEMO_GAMES


class RecordNotFoundError(RuntimeError):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC)


def iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def row_value(row: Any, name: str, default: Any = None) -> Any:
    if isinstance(row, dict):
        return row.get(name, default)
    return getattr(row, name, default)


def decode_list(value: Any) -> list[str]:
    if not isinstance(value, str):
        return []
    try:
        parsed = json.loads(value)
    except ValueError:
        return []
    return [str(item) for item in parsed] if isinstance(parsed, list) else []


def account_from_row(row: Any) -> AccountRecord:
    return AccountRecord(
        id=int(row_value(row, "id")),
        user_id=str(row_value(row, "user_id")),
        steam_id=str(row_value(row, "steam_id")),
        display_name=str(row_value(row, "display_name")),
        profile_url=row_value(row, "profile_url"),
        avatar_url=row_value(row, "avatar_url"),
        is_demo=bool(row_value(row, "is_demo")),
        is_active=bool(row_value(row, "is_active")),
        last_synced_at=parse_datetime(row_value(row, "last_synced_at")),
        created_at=parse_datetime(row_value(row, "created_at")) or utc_now(),
    )


def game_from_row(row: Any) -> GameRecord:
    now = utc_now()
    return GameRecord(
        id=int(row_value(row, "id")),
        account_id=int(row_value(row, "account_id")),
        app_id=int(row_value(row, "app_id")),
        name=str(row_value(row, "name")),
        icon_url=row_value(row, "icon_url"),
        cover_url=str(row_value(row, "cover_url")),
        hero_url=str(row_value(row, "hero_url")),
        playtime_forever=int(row_value(row, "playtime_forever", 0)),
        playtime_2weeks=int(row_value(row, "playtime_2weeks", 0)),
        last_played_at=parse_datetime(row_value(row, "last_played_at")),
        achievements_unlocked=row_value(row, "achievements_unlocked"),
        achievements_total=row_value(row, "achievements_total"),
        tags=decode_list(row_value(row, "tags")),
        moods=decode_list(row_value(row, "moods")),
        favorite=bool(row_value(row, "favorite")),
        custom_status=row_value(row, "custom_status"),
        note=row_value(row, "note"),
        first_seen_at=parse_datetime(row_value(row, "first_seen_at")) or now,
        last_seen_at=parse_datetime(row_value(row, "last_seen_at")) or now,
        updated_at=parse_datetime(row_value(row, "updated_at")) or now,
    )


class D1Store:
    def __init__(self, database: Any) -> None:
        self.database = database

    def _statement(self, query: str, parameters: tuple[Any, ...]) -> Any:
        statement = self.database.prepare(query)
        return statement.bind(*parameters) if parameters else statement

    async def rows(self, query: str, *parameters: Any) -> list[Any]:
        result = await self._statement(query, parameters).all()
        return list(result.results)

    async def first(self, query: str, *parameters: Any) -> Any | None:
        return await self._statement(query, parameters).first()

    async def run(self, query: str, *parameters: Any) -> Any:
        return await self._statement(query, parameters).run()

    async def ensure_user(self, user: SessionUser) -> None:
        now = iso(utc_now())
        await self.run(
            """
            INSERT INTO users (
                google_sub, email, display_name, avatar_url, created_at, last_login_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(google_sub) DO UPDATE SET
                email = excluded.email,
                display_name = excluded.display_name,
                avatar_url = excluded.avatar_url,
                last_login_at = excluded.last_login_at
            """,
            user.sub,
            user.email,
            user.display_name,
            user.avatar_url,
            now,
            now,
        )

    async def active_account(self, user_id: str, *, seed_if_missing: bool = True) -> AccountRecord:
        row = await self.first(
            """
            SELECT * FROM steam_accounts
            WHERE user_id = ? AND is_active = 1
            ORDER BY id DESC LIMIT 1
            """,
            user_id,
        )
        if row is None and seed_if_missing:
            await self.seed_demo(user_id)
            row = await self.first(
                """
                SELECT * FROM steam_accounts
                WHERE user_id = ? AND is_active = 1
                ORDER BY id DESC LIMIT 1
                """,
                user_id,
            )
        if row is None:
            raise RecordNotFoundError("还没有可用的游戏库。")
        return account_from_row(row)

    async def games(self, account_id: int) -> list[GameRecord]:
        rows = await self.rows(
            "SELECT * FROM library_entries WHERE account_id = ?",
            account_id,
        )
        return [game_from_row(row) for row in rows]

    async def update_game(
        self,
        user_id: str,
        app_id: int,
        update: GameUpdate,
    ) -> GameRecord:
        account = await self.active_account(user_id)
        fields: list[str] = []
        values: list[Any] = []
        provided = update.model_fields_set
        if "favorite" in provided:
            fields.append("favorite = ?")
            values.append(int(bool(update.favorite)))
        if "custom_status" in provided:
            fields.append("custom_status = ?")
            values.append(update.custom_status or None)
        if "note" in provided:
            fields.append("note = ?")
            values.append(update.note or None)
        if fields:
            fields.append("updated_at = ?")
            values.append(iso(utc_now()))
            values.extend([account.id, app_id])
            await self.run(
                f"UPDATE library_entries SET {', '.join(fields)} "
                "WHERE account_id = ? AND app_id = ?",
                *values,
            )
        row = await self.first(
            "SELECT * FROM library_entries WHERE account_id = ? AND app_id = ?",
            account.id,
            app_id,
        )
        if row is None:
            raise RecordNotFoundError("游戏不在当前库中。")
        return game_from_row(row)

    async def seed_demo(self, user_id: str) -> AccountRecord:
        steam_id = f"demo-{user_id}"
        now = utc_now()
        row = await self.first(
            "SELECT * FROM steam_accounts WHERE user_id = ? AND steam_id = ?",
            user_id,
            steam_id,
        )
        if row is None:
            row = await self.first(
                """
                INSERT INTO steam_accounts (
                    user_id, steam_id, display_name, avatar_url, is_demo, is_active,
                    last_synced_at, created_at
                ) VALUES (?, ?, ?, ?, 1, 1, ?, ?)
                RETURNING *
                """,
                user_id,
                steam_id,
                "Night Player",
                None,
                iso(now - timedelta(minutes=3)),
                iso(now),
            )
        account = account_from_row(row)
        existing = await self.first(
            "SELECT id FROM library_entries WHERE account_id = ? LIMIT 1",
            account.id,
        )
        if existing is None:
            for index, item in enumerate(DEMO_GAMES):
                unlocked, total = item["achievements"] or (None, None)
                last_played = (
                    now - timedelta(days=item["days_ago"]) if item["days_ago"] is not None else None
                )
                await self.run(
                    """
                    INSERT INTO library_entries (
                        account_id, app_id, name, cover_url, hero_url,
                        playtime_forever, playtime_2weeks, last_played_at,
                        achievements_unlocked, achievements_total, tags, moods, favorite,
                        first_seen_at, last_seen_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    account.id,
                    item["app_id"],
                    item["name"],
                    steam_cover_url(item["app_id"]),
                    steam_hero_url(item["app_id"]),
                    item["minutes"],
                    item["recent"],
                    iso(last_played),
                    unlocked,
                    total,
                    json.dumps(item["tags"], ensure_ascii=False),
                    json.dumps(item["moods"], ensure_ascii=False),
                    int(item["favorite"]),
                    iso(now - timedelta(days=450 - index * 19)),
                    iso(now - timedelta(minutes=3)),
                    iso(now - timedelta(minutes=3)),
                )
        await self.run(
            "UPDATE steam_accounts SET is_active = CASE WHEN id = ? THEN 1 ELSE 0 END "
            "WHERE user_id = ?",
            account.id,
            user_id,
        )
        account.is_active = True
        return account

    async def upsert_steam_account(
        self,
        *,
        user_id: str,
        steam_id: str,
        display_name: str,
        profile_url: str | None,
        avatar_url: str | None,
        synced_at: datetime,
    ) -> AccountRecord:
        row = await self.first(
            """
            INSERT INTO steam_accounts (
                user_id, steam_id, display_name, profile_url, avatar_url,
                is_demo, is_active, last_synced_at, created_at
            ) VALUES (?, ?, ?, ?, ?, 0, 1, ?, ?)
            ON CONFLICT(user_id, steam_id) DO UPDATE SET
                display_name = excluded.display_name,
                profile_url = excluded.profile_url,
                avatar_url = excluded.avatar_url,
                is_active = 1,
                last_synced_at = excluded.last_synced_at
            RETURNING *
            """,
            user_id,
            steam_id,
            display_name,
            profile_url,
            avatar_url,
            iso(synced_at),
            iso(synced_at),
        )
        account = account_from_row(row)
        await self.run(
            "UPDATE steam_accounts SET is_active = CASE WHEN id = ? THEN 1 ELSE 0 END "
            "WHERE user_id = ?",
            account.id,
            user_id,
        )
        return account

    async def upsert_steam_game(
        self,
        *,
        account_id: int,
        app_id: int,
        name: str,
        icon_url: str | None,
        playtime_forever: int,
        playtime_2weeks: int,
        last_played_at: datetime | None,
        seen_at: datetime,
    ) -> None:
        await self.run(
            """
            INSERT INTO library_entries (
                account_id, app_id, name, icon_url, cover_url, hero_url,
                playtime_forever, playtime_2weeks, last_played_at,
                tags, moods, favorite, first_seen_at, last_seen_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, '[]', '[]', 0, ?, ?, ?)
            ON CONFLICT(account_id, app_id) DO UPDATE SET
                name = excluded.name,
                icon_url = excluded.icon_url,
                cover_url = excluded.cover_url,
                hero_url = excluded.hero_url,
                playtime_forever = excluded.playtime_forever,
                playtime_2weeks = excluded.playtime_2weeks,
                last_played_at = excluded.last_played_at,
                last_seen_at = excluded.last_seen_at,
                updated_at = excluded.updated_at
            """,
            account_id,
            app_id,
            name,
            icon_url,
            steam_cover_url(app_id),
            steam_hero_url(app_id),
            playtime_forever,
            playtime_2weeks,
            iso(last_played_at),
            iso(seen_at),
            iso(seen_at),
            iso(seen_at),
        )


def steam_cover_url(app_id: int) -> str:
    return (
        "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/"
        f"{app_id}/library_600x900.jpg"
    )


def steam_hero_url(app_id: int) -> str:
    return (
        "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/"
        f"{app_id}/library_hero.jpg"
    )
