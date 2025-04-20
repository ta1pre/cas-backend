from pydantic import BaseModel, validator
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

class CustomerRsveListItemResponse(BaseModel):
    reservation_id: int
    cast_id: int
    cast_name: str
    status: str
    status_key: str
    start_time: datetime
    course_name: str
    location: Optional[str] = None
    course_price: int
    reservation_fee: int
    traffic_fee: int
    option_list: List[str]
    option_price_list: List[int] = []  # 既存の修正
    total_option_price: int
    total_price: Optional[int] = None
    last_message_time: Optional[datetime] = None
    last_message_preview: Optional[str] = None
    color_code: Optional[str] = None  # 
    course_points: Optional[int] = None  # ← 必須→Optionalに修正

    @validator("course_points", pre=True, always=True)
    def decimal_to_int(cls, v):
        print("【DEBUG】バリデータ input:", v, type(v))
        if v is None:
            return 0
        try:
            return int(v)
        except Exception as e:
            print("【ERROR】course_points変換失敗:", v, type(v), e)
            return 0

class CustomerRsveListResponse(BaseModel):
    page: int  # : 
    limit: int  # : 1
    total_count: Optional[int] = None 
    reservations: List[CustomerRsveListItemResponse]
