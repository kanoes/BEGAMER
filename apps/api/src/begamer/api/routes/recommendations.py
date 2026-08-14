from fastapi import APIRouter

from begamer.api.dependencies import SessionDependency, SettingsDependency
from begamer.schemas import RecommendationRequest, RecommendationResponse
from begamer.services.recommendations import recommend_games

router = APIRouter(tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationResponse)
async def create_recommendation(
    request: RecommendationRequest,
    session: SessionDependency,
    settings: SettingsDependency,
) -> RecommendationResponse:
    return await recommend_games(session, request=request, settings=settings)
