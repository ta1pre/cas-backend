from fastapi import APIRouter, Depends
from app.core.security import get_current_user

# ルーター作成
#sms_router = APIRouter()
#from app.core.security import get_current_user

# ✅ 認証が自動で適用されるルーター
sms_router = APIRouter(
    tags=["SMS"],
    dependencies=[Depends(get_current_user)]  # ✅ 認証を一括適用
)


# 認証コード送信のルーター
from .send_code import router as send_code_router
sms_router.include_router(send_code_router, prefix="/send", tags=["SMS - Send"])

# 認証コード検証のルーター
from .verify_code import router as verify_code_router
sms_router.include_router(verify_code_router, prefix="/verify", tags=["SMS - Verify"])
