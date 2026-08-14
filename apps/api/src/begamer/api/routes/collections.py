from fastapi import APIRouter

from begamer.api.dependencies import SessionDependency
from begamer.schemas import CollectionSuggestion
from begamer.services.collections import suggest_collections
from begamer.services.library import get_active_account

router = APIRouter(tags=["collections"])


@router.get("/collections", response_model=list[CollectionSuggestion])
async def get_collection_suggestions(
    session: SessionDependency,
) -> list[CollectionSuggestion]:
    account = await get_active_account(session)
    return suggest_collections(list(account.library))
