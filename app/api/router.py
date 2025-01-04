from fastapi import APIRouter
from app.api import (
    tiktok_web
)

router = APIRouter()

router.include_router(tiktok_web.router, prefix="")
