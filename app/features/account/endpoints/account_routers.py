from fastapi import APIRouter
account_router = APIRouter()


# JWT関連エンドポイント
from .auth_jwt import router as jwt_router
account_router.include_router(jwt_router, prefix="/auth", tags=["Auth"])

# LINE認証関連エンドポイント
from .auth_line import router as line_router
account_router.include_router(line_router, prefix="/line", tags=["LINE Auth"])
