# change_status_schema.py
from pydantic import BaseModel
from typing import Optional

class ChangeStatusRequest(BaseModel):
    reservation_id: int
    user_id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
