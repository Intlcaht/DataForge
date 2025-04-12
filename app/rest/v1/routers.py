from rest.v1.endpoints import items, db_management, obfuscator, utils
from fastapi import APIRouter

api_v1_router = APIRouter()

# API endpoints
api_v1_router.include_router(
    items.router,
    prefix="/items",
    tags=["items"]
)

api_v1_router.include_router(
    db_management.router,
    prefix="/db",
    tags=["DB"]
)

api_v1_router.include_router(
    obfuscator.router,
    prefix="/ob",
    tags=["Obfuscator"]
)

api_v1_router.include_router(
    utils.router,
    prefix="/utl",
    tags=["Tasks"]
)