"""Admin Cast routers"""
from fastapi import APIRouter, Depends

from app.core.security import get_current_user

from .cast_list import router as cast_list_router
from .identity_documents import router as identity_docs_router
from .cast_status import router as cast_status_router

# 認証必須のAdminキャスト管理ルーター
admin_cast_router = APIRouter(
    prefix="",
    tags=["Admin - Cast"],
    dependencies=[Depends(get_current_user)]  # 認証
)

# 一覧取得
admin_cast_router.include_router(cast_list_router, prefix="")
# 身分証画像取得
admin_cast_router.include_router(identity_docs_router, prefix="")
# ステータス更新
admin_cast_router.include_router(cast_status_router, prefix="")
