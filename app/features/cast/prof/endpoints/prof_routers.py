# Cast Profile Routers
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

# 認証付きルーターを作成
prof_router = APIRouter(
    dependencies=[Depends(get_current_user)],
    tags=["Cast - Profile"] # APIドキュメント用のタグ
)

# prof_endpoint.py で定義されたルーターをインクルード
from . import prof_endpoint # prof_endpoint をインポート

# prefixはendpoint側で指定してているのでここでは不要
prof_router.include_router(prof_endpoint.router, prefix="", tags=["Cast - Profile API"])
