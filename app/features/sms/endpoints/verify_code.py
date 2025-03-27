from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.features.sms.repositories.sms_repository import SMSRepository
from app.features.sms.schemas.sms_schema import VerifyCodeRequest
from app.core.security import get_current_user

router = APIRouter()

@router.post("/")
def verify_code(
    request: VerifyCodeRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)  # ✅ 認証済みユーザーのみ
):
    """
    ✅ 認証コードを検証して電話番号を認証済みにする
    """
    sms_repo = SMSRepository(db)

    if not sms_repo.verify_code(user_id=user_id, code=request.code):
        raise HTTPException(status_code=400, detail="認証コードが間違っています")

    return {"message": "電話番号認証が完了しました"}
