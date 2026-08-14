from fastapi import APIRouter

from begamer.api.dependencies import SessionDependency
from begamer.schemas import DashboardResponse
from begamer.services.library import dashboard

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(session: SessionDependency) -> DashboardResponse:
    return await dashboard(session)
