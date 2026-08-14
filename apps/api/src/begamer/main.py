from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from begamer.api.router import api_router
from begamer.clients.steam import SteamClientError
from begamer.core.config import Settings, get_settings
from begamer.db.session import Database
from begamer.services.library import LibraryNotFoundError
from begamer.services.seed import seed_demo_library


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database = Database(app_settings.database_url)
        app.state.database = database
        if app_settings.auto_create_database:
            await database.create_all()
        if app_settings.seed_demo_data:
            async with database.sessions() as session:
                await seed_demo_library(session)
        yield
        await database.dispose()

    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.app_version,
        description="Local-first Steam library curator API",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url=None,
    )
    app.state.settings = app_settings
    allowed_origins = {
        app_settings.frontend_origin,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    }
    app.add_middleware(
        CORSMiddleware,
        allow_origins=sorted(allowed_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    app.include_router(api_router, prefix=app_settings.api_prefix)

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {"name": app_settings.app_name, "docs": "/api/docs"}

    @app.exception_handler(LibraryNotFoundError)
    async def library_not_found(_request: Request, error: LibraryNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "LIBRARY_NOT_FOUND", "message": str(error)}},
        )

    @app.exception_handler(SteamClientError)
    async def steam_error(_request: Request, error: SteamClientError) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={"error": {"code": error.code, "message": str(error)}},
        )

    return app


app = create_app()
