from pydantic import BaseModel
from typing import List, Optional

class StationSuggestRequest(BaseModel):
    query: str

class StationSuggestResponse(BaseModel):
    id: int
    name: str
    line_name: str | None = None  # 複数乗り入れの場合はNone

class StationUpdateRequest(BaseModel):
    reservation_id: int
    cast_id: int
    station_id: Optional[int] = None

class StationUpdateResponse(BaseModel):
    success: bool
    message: str
