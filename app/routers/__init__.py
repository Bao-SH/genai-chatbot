from fastapi import APIRouter
from . import chat, health

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/api")
api_router.include_router(health.router, prefix="/api")
