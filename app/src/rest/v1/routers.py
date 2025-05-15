from rest.v1.endpoints import db_management, obfuscator, utils
from fastapi import APIRouter

api_v1_router = APIRouter()

api_v1_router.include_router(
    db_management.router,
    prefix="/db",
    tags=["DB"]
)

api_v1_router.include_router(
    obfuscator.router,
    prefix="/sec",
    tags=["Obfuscator"]
)

api_v1_router.include_router(
    utils.router,
    prefix="/fns",
    tags=["Tasks"]
)