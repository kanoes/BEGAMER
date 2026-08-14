from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from begamer.db.models import Base


def ensure_database_directory(url: str) -> None:
    marker = "sqlite+aiosqlite:///"
    if not url.startswith(marker):
        return
    path = url.removeprefix(marker)
    if path and path != ":memory:":
        Path(path).expanduser().parent.mkdir(parents=True, exist_ok=True)


class Database:
    def __init__(self, url: str) -> None:
        self.url = url
        ensure_database_directory(url)

        engine_options: dict[str, Any] = {"pool_pre_ping": True}
        if url.startswith("sqlite+aiosqlite"):
            engine_options["connect_args"] = {"check_same_thread": False}

        self.engine: AsyncEngine = create_async_engine(url, **engine_options)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)

        if url.startswith("sqlite+aiosqlite"):
            self._configure_sqlite()

    def _configure_sqlite(self) -> None:
        @event.listens_for(self.engine.sync_engine, "connect")
        def set_sqlite_pragmas(connection: Connection, _record: object) -> None:
            cursor = connection.cursor()  # type: ignore[attr-defined]
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()

    async def create_all(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self.sessions() as session:
            yield session
