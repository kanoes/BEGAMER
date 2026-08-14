from fastapi import APIRouter

from begamer.api.dependencies import SessionDependency, SettingsDependency
from begamer.schemas import CapabilityResponse, HealthResponse
from begamer.services.library import get_active_account

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health(settings: SettingsDependency) -> HealthResponse:
    return HealthResponse(status="ok", version=settings.app_version)


@router.get("/capabilities", response_model=CapabilityResponse)
async def capabilities(
    session: SessionDependency,
    settings: SettingsDependency,
) -> CapabilityResponse:
    account = await get_active_account(session)
    return CapabilityResponse(
        steam_configured=bool(settings.steam_web_api_key),
        llm_configured=bool(settings.openai_api_key),
        llm_model=settings.openai_model,
        active_source="demo" if account.is_demo else "steam",
    )
