# 📂 app/features/reserve/schemas/cast_rsvelist_schema.py

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CastRsveListItemResponse(BaseModel):
    reservation_id: int
    user_id: int
    user_name: str  # ✅ 顧客名
    status: str
    status_key: str
    start_time: datetime
    course_name: str
    location: Optional[str] = None
    station_name: Optional[str] = None
    course_price: int
    traffic_fee: int
    last_message_time: Optional[datetime] = None
    last_message_preview: Optional[str] = None
    color_code: Optional[str] = None

class CastRsveListResponse(BaseModel):
    page: int
    limit: int
    total_count: int
    reservations: List[CastRsveListItemResponse]
