# app/features/customer/area/endpoints/area_routers.py

from fastapi import APIRouter, Depends
from app.core.security import get_current_user

# ✅ ルーターの作成（認証必須）
castprof_router = APIRouter(
    tags=["Customer - Area"],
    dependencies=[Depends(get_current_user)]
)

from fastapi import APIRouter, Depends
from app.core.security import get_current_user

# ✅ ルーターの作成（認証必須）
area_router = APIRouter(  # ← ここを修正（castprof_router → area_router に統一）
    tags=["Customer - Area"],
    dependencies=[Depends(get_current_user)]
)

from app.features.customer.area.endpoints import area as area_api_router
area_router.include_router(area_api_router.router, prefix="", tags=["Customer - Area API"])

from . import station as station_api_router
area_router.include_router(station_api_router.router, prefix="", tags=["Customer - Area API"])

from app.features.customer.area.endpoints.suggest import router as suggest_router
area_router.include_router(suggest_router, prefix="", tags=["Customer - Area API"])
