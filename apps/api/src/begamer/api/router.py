from fastapi import APIRouter

from begamer.api.routes import collections, dashboard, games, recommendations, steam, system

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(dashboard.router)
api_router.include_router(games.router)
api_router.include_router(collections.router)
api_router.include_router(recommendations.router)
api_router.include_router(steam.router)
