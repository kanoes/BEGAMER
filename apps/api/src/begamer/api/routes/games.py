from typing import Annotated, Literal

from fastapi import APIRouter, Query

from begamer.api.dependencies import SessionDependency
from begamer.schemas import GameListResponse, GameRead, GameStatus, GameUpdate
from begamer.services.library import list_games, update_game

router = APIRouter(prefix="/games", tags=["games"])


@router.get("", response_model=GameListResponse)
async def get_games(
    session: SessionDependency,
    q: Annotated[str | None, Query(max_length=120)] = None,
    status: GameStatus | None = None,
    favorite: bool | None = None,
    sort: Literal["name", "playtime", "recent", "added"] = "playtime",
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 48,
) -> GameListResponse:
    return await list_games(
        session,
        query=q,
        status=status,
        favorite=favorite,
        sort=sort,
        page=page,
        page_size=page_size,
    )


@router.patch("/{app_id}", response_model=GameRead)
async def patch_game(
    app_id: int,
    update: GameUpdate,
    session: SessionDependency,
) -> GameRead:
    return await update_game(session, app_id=app_id, update=update)
