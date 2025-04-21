from fastapi import APIRouter

from src.app.routers import router

main_router = APIRouter()

main_router.include_router(router)
