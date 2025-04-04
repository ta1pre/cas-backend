# app/features/customer/user_profile/schemas/user_profile_schema.py

from pydantic import BaseModel
from typing import Optional

# ユーザープロフィール情報のスキーマ
class UserProfileResponse(BaseModel):
    id: int
    nick_name: Optional[str] = None
    line_id: str
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    mobile_phone: Optional[str] = None
    phone_verified: Optional[bool] = None
    picture_url: Optional[str] = None
    sex: Optional[str] = None
    birth: Optional[str] = None
    user_type: Optional[str] = None
    
    class Config:
        orm_mode = True

# ニックネーム更新リクエスト用スキーマ
class UpdateNicknameRequest(BaseModel):
    nick_name: str

# ニックネーム更新レスポンス用スキーマ
class UpdateNicknameResponse(BaseModel):
    message: str
    nick_name: str
