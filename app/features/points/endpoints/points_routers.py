#app/features/points/endpoints/points_routers.py

# ✅ media_routers.py - メディア関連ルーター
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

# ✅ 認証が自動で適用されるメディアルーター
media_router = APIRouter(
    tags=["Points"],
    dependencies=[Depends(get_current_user)]  # ✅ 認証を一括適用
)

# ✅ ポイント処理
from app.features.points.endpoints.points import router as points_routers
media_router.include_router(points_routers, prefix="", tags=["Points"])

