from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

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
    color_code: Optional[str] = None  # ✅ 新しく追加する部分

class CustomerRsveListResponse(BaseModel):
    page: int  # ✅ 追加: 取得ページ番号
    limit: int  # ✅ 追加: 1ページあたりの取得件数
    total_count: Optional[int] = None 
    reservations: List[CustomerRsveListItemResponse]

