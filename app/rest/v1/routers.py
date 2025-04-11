from .endpoints import health, items
from fastapi import APIRouter

api_v1_router = APIRouter()

# Health check endpoint
api_v1_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

# API endpoints
api_v1_router.include_router(
    items.router,
    prefix="/items",
    tags=["items"]
)