# app/features/customer/castprof/endpoints/castprof_routers.py

from fastapi import APIRouter, Depends
from app.core.security import get_current_user

# ✅ ルーターの作成（認証必須）
castprof_router = APIRouter(
    tags=["Customer - CastProf"],
    dependencies=[Depends(get_current_user)]
)

import app.features.customer.castprof.endpoints.castprof as castprof_api_router
castprof_router.include_router(castprof_api_router.router, prefix="", tags=["Customer - CastProf API"])
