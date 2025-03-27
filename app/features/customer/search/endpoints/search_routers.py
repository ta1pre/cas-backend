# app/features/customer/search/endpoints/search_routers.py

from fastapi import APIRouter, Depends
from app.core.security import get_current_user

# ✅ ルーターの作成（認証必須）
search_router = APIRouter(
    tags=["Customer - Search"],
    dependencies=[Depends(get_current_user)]
)

import app.features.customer.search.endpoints.search as search_api_router
search_router.include_router(search_api_router.router, prefix="", tags=["Customer - Search API"])
