from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.features.tenant.schemas.auth import TenantLoginRequest, TenantLoginResponse
from app.core.security import verify_password, create_access_token
from app.db.session import get_db
from app.db.models.user import User

router = APIRouter()

@router.post("/login", response_model=TenantLoginResponse)
async def tenant_login(data: TenantLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email, User.user_type == 'tenant').first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが正しくありません")
    token = create_access_token(user_id=str(user.id), user_type=user.user_type)
    return TenantLoginResponse(access_token=token, token_type="bearer")
