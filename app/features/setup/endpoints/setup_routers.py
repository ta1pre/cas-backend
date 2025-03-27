from fastapi import APIRouter, Depends
from app.core.security import get_current_user  

# ✅ 認証が自動で適用されるルーター
setup_router = APIRouter(
    dependencies=[Depends(get_current_user)],
    tags=["Setup"]  # ✅ Setup機能のタグを追加
)

# ステータス
from .setup_status import router as status_router
setup_router.include_router(status_router, prefix="/status", tags=["Setup - Status"])

#登録
from .setup_register import router as register_router
setup_router.include_router(register_router, prefix="/register", tags=["Setup - Register"])




