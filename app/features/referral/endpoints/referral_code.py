from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.core.security import get_current_user

router = APIRouter()

@router.post("/get_code", summary="紹介コード（invitation_id）を取得")
def get_referral_code(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    ログインユーザーのinvitation_id（紹介コード）を返却
    """
    if not current_user or not current_user.invitation_id:
        raise HTTPException(status_code=404, detail="紹介コードが見つかりません")
    return {"invitation_id": current_user.invitation_id}
