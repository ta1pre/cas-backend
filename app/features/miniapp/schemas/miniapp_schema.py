# app/features/miniapp/schemas/miniapp_schema.py

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class UserRegistrationRequest(BaseModel):
    """ユーザー登録リクエスト"""
    id_token: str = Field(..., description="LIFF IDトークン")
    user_type: Literal["cast", "customer"] = Field(..., description="ユーザータイプ")
    tracking_id: Optional[str] = Field(None, description="招待コード")

class UserRegistrationResponse(BaseModel):
    """ユーザー登録レスポンス"""
    success: bool = Field(..., description="成功フラグ")
    message: str = Field(..., description="メッセージ")
    user_id: Optional[int] = Field(None, description="ユーザーID")
    user_type: Optional[str] = Field(None, description="ユーザータイプ")
    is_new_user: bool = Field(..., description="新規ユーザーかどうか")

class LiffUserInfo(BaseModel):
    """LIFF から取得したユーザー情報"""
    line_id: str = Field(..., description="LINE ユーザーID")
    display_name: str = Field(..., description="表示名")
    picture_url: Optional[str] = Field(None, description="プロフィール画像URL")

class UserUpdateRequest(BaseModel):
    """ユーザー情報更新リクエスト"""
    user_type: Literal["cast", "customer"] = Field(..., description="ユーザータイプ")

class ErrorResponse(BaseModel):
    """エラーレスポンス"""
    success: bool = Field(False, description="成功フラグ")
    message: str = Field(..., description="エラーメッセージ")
    error_code: Optional[str] = Field(None, description="エラーコード")