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
from app.features.points.endpoints.points import router as points_router
media_router.include_router(points_router, prefix="", tags=["Points"])

# ✅ 管理画面用ポイント処理
from app.features.points.endpoints.admin_points import router as admin_points_router
media_router.include_router(admin_points_router, prefix="/admin", tags=["Admin Points"])

