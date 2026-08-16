from typing import Annotated, Literal

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse

from begamer_worker.auth import (
    attach_session,
    auth_required,
    clear_session,
    current_user,
    env_text,
    request_env,
    verify_google_credential,
)
from begamer_worker.catalog import (
    account_read,
    dashboard,
    game_list,
    game_read,
    suggest_collections,
)
from begamer_worker.recommendations import recommend_games
from begamer_worker.schemas import (
    AccountRead,
    AuthConfig,
    CapabilityResponse,
    CollectionSuggestion,
    DashboardResponse,
    GameListResponse,
    GameRead,
    GameStatus,
    GameUpdate,
    GoogleCredential,
    HealthResponse,
    RecommendationRequest,
    RecommendationResponse,
    SessionUser,
    SyncRequest,
    SyncResponse,
)
from begamer_worker.steam import SteamClientError, sync_steam_library
from begamer_worker.storage import D1Store, RecordNotFoundError

API_PREFIX = "/api/v1"


def store_from_request(request: Request) -> D1Store:
    return D1Store(request_env(request).DB)


async def authenticated_user(request: Request) -> SessionUser:
    user = current_user(request)
    await store_from_request(request).ensure_user(user)
    return user


StoreDependency = Annotated[D1Store, Depends(store_from_request)]
UserDependency = Annotated[SessionUser, Depends(authenticated_user)]

app = FastAPI(
    title="BEGAMER API",
    version="0.2.0",
    description="Personal Steam library curator on Cloudflare Workers",
    docs_url="/api/docs",
    redoc_url=None,
)
router = APIRouter(prefix=API_PREFIX)


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.2.0")


@router.get("/auth/config", response_model=AuthConfig, tags=["auth"])
async def auth_config(request: Request) -> AuthConfig:
    env = request_env(request)
    return AuthConfig(
        auth_required=auth_required(env),
        google_client_id=env_text(env, "GOOGLE_CLIENT_ID"),
    )


@router.post("/auth/google", response_model=SessionUser, tags=["auth"])
async def google_login(
    payload: GoogleCredential,
    request: Request,
    response: Response,
) -> SessionUser:
    env = request_env(request)
    user = await verify_google_credential(payload.credential, env)
    await store_from_request(request).ensure_user(user)
    attach_session(response, user, env)
    return user


@router.get("/auth/me", response_model=SessionUser, tags=["auth"])
async def auth_me(user: UserDependency) -> SessionUser:
    return user


@router.post("/auth/logout", status_code=204, tags=["auth"])
async def logout(response: Response) -> None:
    clear_session(response)


@router.get("/capabilities", response_model=CapabilityResponse, tags=["system"])
async def capabilities(
    request: Request,
    store: StoreDependency,
    user: UserDependency,
) -> CapabilityResponse:
    env = request_env(request)
    account = await store.active_account(user.sub)
    return CapabilityResponse(
        steam_configured=bool(env_text(env, "STEAM_WEB_API_KEY")),
        llm_configured=bool(env_text(env, "OPENAI_API_KEY")),
        llm_model=env_text(env, "OPENAI_MODEL", "gpt-5.6-luna") or "gpt-5.6-luna",
        active_source="demo" if account.is_demo else "steam",
    )


@router.get("/dashboard", response_model=DashboardResponse, tags=["dashboard"])
async def get_dashboard(
    store: StoreDependency,
    user: UserDependency,
) -> DashboardResponse:
    account = await store.active_account(user.sub)
    return dashboard(account, await store.games(account.id))


@router.get("/games", response_model=GameListResponse, tags=["games"])
async def get_games(
    store: StoreDependency,
    user: UserDependency,
    q: Annotated[str | None, Query(max_length=120)] = None,
    status: GameStatus | None = None,
    favorite: bool | None = None,
    sort: Literal["name", "playtime", "recent", "added"] = "playtime",
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 48,
) -> GameListResponse:
    account = await store.active_account(user.sub)
    return game_list(
        await store.games(account.id),
        query=q,
        status=status,
        favorite=favorite,
        sort=sort,
        page=page,
        page_size=page_size,
    )


@router.patch("/games/{app_id}", response_model=GameRead, tags=["games"])
async def patch_game(
    app_id: int,
    update: GameUpdate,
    store: StoreDependency,
    user: UserDependency,
) -> GameRead:
    return game_read(await store.update_game(user.sub, app_id, update))


@router.get("/collections", response_model=list[CollectionSuggestion], tags=["collections"])
async def get_collections(
    store: StoreDependency,
    user: UserDependency,
) -> list[CollectionSuggestion]:
    account = await store.active_account(user.sub)
    return suggest_collections(await store.games(account.id))


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    tags=["recommendations"],
)
async def create_recommendation(
    payload: RecommendationRequest,
    request: Request,
    store: StoreDependency,
    user: UserDependency,
) -> RecommendationResponse:
    account = await store.active_account(user.sub)
    return await recommend_games(
        await store.games(account.id),
        request=payload,
        env=request_env(request),
    )


@router.post("/steam/sync", response_model=SyncResponse, tags=["steam"])
async def sync_library(
    payload: SyncRequest,
    request: Request,
    store: StoreDependency,
    user: UserDependency,
) -> SyncResponse:
    env = request_env(request)
    steam_id = payload.steam_id or env_text(env, "STEAM_ID")
    api_key = env_text(env, "STEAM_WEB_API_KEY")
    if steam_id is None or not steam_id.isdigit() or len(steam_id) != 17:
        raise HTTPException(status_code=409, detail="请提供有效的 17 位 SteamID64。")
    if api_key is None:
        raise HTTPException(status_code=409, detail="请先配置 STEAM_WEB_API_KEY。")
    return await sync_steam_library(
        store,
        user_id=user.sub,
        steam_id=steam_id,
        api_key=api_key,
    )


@router.post("/steam/demo", response_model=AccountRead, tags=["steam"])
async def use_demo_library(
    store: StoreDependency,
    user: UserDependency,
) -> AccountRead:
    return account_read(await store.seed_demo(user.sub))


app.include_router(router)


@app.exception_handler(RecordNotFoundError)
async def not_found(_request: Request, error: RecordNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "RECORD_NOT_FOUND", "message": str(error)}},
    )


@app.exception_handler(SteamClientError)
async def steam_error(_request: Request, error: SteamClientError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"error": {"code": error.code, "message": str(error)}},
    )


@app.exception_handler(Exception)
async def unexpected_error(_request: Request, _error: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "请求暂时无法完成，请稍后重试。",
            }
        },
    )
