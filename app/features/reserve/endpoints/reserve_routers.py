# app/features/reserve/endpoints/reserve_routers.py

from fastapi import APIRouter, Depends
from app.core.security import get_current_user

# ルーターのインスタンスを作成
reserve_router = APIRouter(
    tags=["Reserve"],
    dependencies=[Depends(get_current_user)]  # 認証を適用
)

# 各エンドポイントのルーターをインポート
from app.features.reserve.endpoints.customer import customer_router
from app.features.reserve.endpoints.cast import cast_router
from app.features.reserve.endpoints.common import common_router

# ルーターを統合
reserve_router.include_router(customer_router, prefix="/customer", tags=["Customer"])
reserve_router.include_router(cast_router, prefix="/cast", tags=["Cast"])
reserve_router.include_router(common_router, prefix="/common", tags=["Common"])