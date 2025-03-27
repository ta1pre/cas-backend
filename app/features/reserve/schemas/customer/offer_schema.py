from pydantic import BaseModel
from typing import Optional, Union

class OfferReservationCreate(BaseModel):
    castId: int
    userId: int
    courseName: str
    courseType: int
    date: Optional[Union[str, None]] = None
    message: Optional[str] = ""
    station: int
    time: Optional[Union[str, None]] = None
    timeOption: str  # "fast" or "custom"
    latitude: Optional[float] = None  # ✅ 追加
    longitude: Optional[float] = None  # ✅ 追加

class OfferReservationResponse(BaseModel):
    reservation_id: int
    status: str
