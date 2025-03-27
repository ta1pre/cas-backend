from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.features.sms.repositories.sms_repository import SMSRepository
from app.features.sms.schemas.sms_schema import SendCodeRequest
from app.core.security import get_current_user  # ✅ 認証ユーザーの取得
import random

router = APIRouter()

@router.post("/")
def send_verification_code(
    request: SendCodeRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)  # ✅ トークンから`user_id`を取得
):
    """
    ✅ 認証コードの送信（DB保存 & AWS SNSでSMS送信）
    """
    auth_code = str(random.randint(1000, 9999))  # ✅ 4桁の認証コード
    sms_repo = SMSRepository(db)

    success = sms_repo.save_verification_code(user_id=user_id, phone=request.phone, code=auth_code)

    if not success:
        raise HTTPException(status_code=500, detail="認証コードの送信に失敗しました")

    return {"message": "認証コードをSMSで送信しました"}
