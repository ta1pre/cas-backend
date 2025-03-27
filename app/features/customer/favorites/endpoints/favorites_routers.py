# app/features/customer/favorites/endpoints/favorites_routers.py

from fastapi import APIRouter, Depends
from app.core.security import get_current_user

# ✅ ルーターの作成（認証必須）
favorites_router = APIRouter(
    tags=["Customer - Favorites"],
    dependencies=[Depends(get_current_user)]
)

import app.features.customer.favorites.endpoints.favorites as favorites_api_router
favorites_router.include_router(favorites_api_router.router, prefix="", tags=["Customer - Favorites API"])
