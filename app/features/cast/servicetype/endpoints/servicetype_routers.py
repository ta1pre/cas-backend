from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from .servicetype import router as servicetype_api_router  # ← 名前を変更して区別

# ✅ 認証を一括適用するルーター
servicetype_router = APIRouter(
    tags=["ServiceType"],
    dependencies=[Depends(get_current_user)]
)

# ✅ `servicetype.py` のエンドポイントを追加
servicetype_router.include_router(servicetype_api_router, prefix="", tags=["ServiceType"])
