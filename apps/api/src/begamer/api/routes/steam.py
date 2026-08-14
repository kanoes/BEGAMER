from fastapi import APIRouter, HTTPException

from begamer.api.dependencies import SessionDependency, SettingsDependency
from begamer.schemas import AccountRead, SyncRequest, SyncResponse
from begamer.services.library import account_read
from begamer.services.seed import activate_demo_library
from begamer.services.steam_sync import sync_steam_library

router = APIRouter(prefix="/steam", tags=["steam"])


@router.post("/sync", response_model=SyncResponse)
async def sync_library(
    request: SyncRequest,
    session: SessionDependency,
    settings: SettingsDependency,
) -> SyncResponse:
    steam_id = request.steam_id or settings.steam_id
    if steam_id is None:
        raise HTTPException(status_code=409, detail="请提供 SteamID64，或在 .env 配置 STEAM_ID。")
    try:
        return await sync_steam_library(session, settings=settings, steam_id=steam_id)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/demo", response_model=AccountRead)
async def use_demo_library(session: SessionDependency) -> AccountRead:
    account = await activate_demo_library(session)
    return account_read(account)
