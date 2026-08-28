from fastapi import APIRouter

from app.api.v1.endpoints import daily

router = APIRouter(prefix="/api/v1")

router.include_router(daily.router)