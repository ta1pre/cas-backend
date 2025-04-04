# app/features/customer/user_profile/endpoints/user_profile.py

from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.features.customer.user_profile.service.user_profile_service import get_user_profile, update_user_nickname
from app.features.customer.user_profile.schemas.user_profile_schema import UserProfileResponse, UpdateNicknameRequest, UpdateNicknameResponse
from app.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter()

class UserIdRequest(BaseModel):
    user_id: int

@router.post("/profile", response_model=UserProfileResponse)
def fetch_user_profile(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user)):
    """
    ユーザープロフィール情報を取得する
    現在認証されているユーザーのプロフィール情報を返す
    """
    return get_user_profile(current_user_id, db)

@router.post("/update_profile", response_model=UpdateNicknameResponse)
def update_profile(update_data: UpdateNicknameRequest = Body(...), db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user)):
    """
    ニックネームを更新する
    現在認証されているユーザーのニックネームを更新する
    """
    return update_user_nickname(current_user_id, update_data.nick_name, db)
