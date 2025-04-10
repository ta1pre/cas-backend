from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.security import create_access_token, create_refresh_token
from app.db.session import get_db
from app.db.models.user import User

router = APIRouter(tags=["Admin - TestLogin"])

# ✅ リクエストボディ用のスキーマ
class TestLoginRequest(BaseModel):
    user_id: int

@router.post("/login")
def test_login(request: TestLoginRequest, db: Session = Depends(get_db)):
    """
    ✅ 任意の `user_id` を指定して強制ログイン
    ✅ 通常のログインと同じ JWT を発行
    ✅ `refresh_token` も発行
    """
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ JWT トークンを発行
    access_token = create_access_token(user_id=str(user.id), user_type=user.user_type, affi_type=user.affi_type)
    refresh_token = create_refresh_token(user_id=str(user.id))  # ✅ リフレッシュトークンを追加

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # ✅ 追加
        "token_type": "bearer"
    }

@router.post("/login_nopw")
def test_login_nopw(request: TestLoginRequest, db: Session = Depends(get_db)):
    """
    ✅ [認証不要] 任意の `user_id` を指定して強制ログイン
    ✅ 通常のログインと同じ JWT を発行
    ✅ `refresh_token` も発行
    """
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ JWT トークンを発行
    access_token = create_access_token(user_id=str(user.id), user_type=user.user_type, affi_type=user.affi_type)
    refresh_token = create_refresh_token(user_id=str(user.id))  # ✅ リフレッシュトークンを追加

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # ✅ 追加
        "token_type": "bearer"
    }
