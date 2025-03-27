# 📂 app/features/reserve/schemas/cast/cast_detail_schema.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class OptionDetail(BaseModel):
    """予約オプション詳細"""
    option_id: int
    name: str
    price: int
    is_custom: bool

class CastReservationDetailResponse(BaseModel):
    """予約詳細レスポンススキーマ"""
    reservation_id: int
    user_name: str
    course_name: str
    start_time: datetime
    end_time: datetime
    location: str
    station_name: Optional[str] = Field(None, description="最寄り駅名")
    latitude: Optional[float]
    longitude: Optional[float]
    
    # 料金情報
    designation_fee: int = Field(0, description="指名料")
    options_fee: int = Field(0, description="オプション料金合計")
    traffic_fee: int = Field(..., description="交通費")
    reservation_fee: int = Field(..., description="予約基本料金")
    course_fee: int = Field(..., description="コース料金（キャスト報酬）")
    total_points: int = Field(..., description="合計金額（ポイント）")
    
    # オプション詳細
    options: List[OptionDetail] = Field(default=[], description="選択されたオプション一覧")
    
    status: str
    color_code: Optional[str] = Field(None, description="ステータスの色コード")
    cast_label: Optional[str] = Field(None, description="キャスト向けステータス表示")
    description: Optional[str] = Field(None, description="ステータスの説明")
    reservation_note: Optional[str]
    cancel_reason: Optional[str]
