from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CustomOption(BaseModel):
    """カスタムオプション定義スキーマ"""
    name: str = Field(..., description="カスタムオプション名")
    price: int = Field(..., description="オプション価格")


class CastReservationEditRequest(BaseModel):
    """予約編集リクエストスキーマ"""
    reservation_id: int = Field(..., description="予約ID")
    cast_id: int = Field(..., description="キャストID")
    course_id: int = Field(..., description="コースID")  
    start_time: datetime = Field(..., description="施術開始時間")
    end_time: datetime = Field(..., description="施術終了時間")
    location: str = Field(..., description="施術場所（駅IDまたは緯度,経度）")
    reservation_note: Optional[str] = Field(None, description="予約メモ")
    status: str = Field("waiting_user_confirm", description="予約ステータス")
    option_ids: List[int] = Field(default=[], description="選択オプションIDリスト")
    custom_options: List[CustomOption] = Field(default=[], description="カスタムオプションリスト")
    # ★ 追加: 交通費フィールド
    transportation_fee: Optional[int] = Field(None, description="交通費") 


class CastReservationEditResponse(BaseModel):
    """予約編集レスポンススキーマ"""
    success: bool = Field(..., description="成功フラグ")
    message: str = Field(..., description="メッセージ")
    reservation_id: int = Field(..., description="予約ID")
