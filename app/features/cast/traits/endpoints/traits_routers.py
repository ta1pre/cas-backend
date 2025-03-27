from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from .traits import router as traits_api_router  

# ✅ 認証を一括適用するルーター
traits_router = APIRouter(
    tags=["Traits"],
    dependencies=[Depends(get_current_user)]
)

# ✅ `traits.py` のエンドポイントを追加
traits_router.include_router(traits_api_router, prefix="/traits", tags=["Traits"])
