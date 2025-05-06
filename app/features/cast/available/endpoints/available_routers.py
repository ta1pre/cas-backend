from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from .update_available import router as update_router

available_router = APIRouter(
    prefix="/available",
    tags=["Cast - Available"],
    dependencies=[Depends(get_current_user)]
)
available_router.include_router(update_router, prefix="/update")
