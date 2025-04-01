from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.features.posts.endpoints.post_endpoints import router as post_router

# 認証が適用されるルーター
posts_router = APIRouter(
    dependencies=[Depends(get_current_user)],  # ここで認証を適用
    tags=["Posts"]
)

# 投稿用のエンドポイントをインクルード
posts_router.include_router(post_router, prefix="", tags=["Posts"])
