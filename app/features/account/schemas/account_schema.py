from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

# ---------------------------
# 🚀 共通シリアライザ (Base)
# ---------------------------
class UserBase(BaseModel):
    nick_name: Optional[str] = Field(None, example="Taro")
    prefectures: Optional[str] = Field(None, example="Tokyo")
    email: Optional[EmailStr] = Field(None, example="taro@example.com")
    email_verified: Optional[bool] = Field(False, example=True)
    phone_verified: Optional[bool] = Field(False, example=True)
    mobile_phone: Optional[str] = Field(None, example="090-1234-5678")
    picture_url: Optional[str] = Field(None, example="https://example.com/picture.jpg")
    sex: Optional[str] = Field(None, example="Male")
    birth: Optional[str] = Field(None, example="1990-01-01")
    user_type: Optional[str] = Field(None, example="User")
    affi_type: Optional[int] = Field(None, example=1)
    last_login: Optional[str] = Field(None, example="2024-01-02 14:00:00")


# ✅ ユーザープロフィール更新用
class UserUpdate(UserBase):
    line_id: str = Field(..., example="abc123")


# ✅ 新規ユーザー登録用
class UserCreate(UserBase):
    line_id: str = Field(..., example="abc123")
    password: Optional[str] = Field(None, example="password123")


# ✅ ユーザー基本情報レスポンス
class UserResponse(UserBase):
    id: int = Field(..., example=1)
    line_id: str = Field(..., example="abc123")
    invitation_id: Optional[str] = Field(None, example="INV123")
    tracking_id: Optional[str] = Field(None, example="TRACK456")
    created_at: Optional[datetime] = Field(None, example="2024-01-02T14:00:00")
    updated_at: Optional[datetime] = Field(None, example="2024-01-02T14:00:00")

    class Config:
        orm_mode = True
