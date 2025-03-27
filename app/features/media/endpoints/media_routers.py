# ✅ media_routers.py - メディア関連ルーター
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

# ✅ 認証が自動で適用されるメディアルーター
media_router = APIRouter(
    tags=["Media"],
    dependencies=[Depends(get_current_user)]  # ✅ 認証を一括適用
)

# ✅ 写真アップロード用エンドポイント
from app.features.media.endpoints.media_upload import router as media_upload_router
media_router.include_router(media_upload_router, prefix="/upload", tags=["Media - Upload"])

# ✅ メディアファイル取得用エンドポイント（将来的に拡張可能）
#from app.features.media.endpoints.media_fetch import router as media_fetch_router
#media_router.include_router(media_fetch_router, prefix="/fetch", tags=["Media - Fetch"])

