from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.features.tenant.schemas.auth import TenantLoginRequest, TenantLoginResponse
from app.core.security import verify_password, create_access_token, create_refresh_token  # create_refresh_tokenを追加
from app.db.session import get_db
from app.db.models.user import User

router = APIRouter()

@router.post("/login", response_model=TenantLoginResponse)
async def tenant_login(data: TenantLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email, User.user_type == 'tenant').first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが正しくありません")
    # アクセストークンとリフレッシュトークンを生成
    access_token = create_access_token(user_id=str(user.id), user_type=user.user_type)
    refresh_token = create_refresh_token(user_id=str(user.id))  # リフレッシュトークンを生成
    
    # 両方のトークンをレスポンスに含める
    return TenantLoginResponse(
        access_token=access_token, 
        refresh_token=refresh_token,  # リフレッシュトークンを追加
        token_type="bearer"
    )
