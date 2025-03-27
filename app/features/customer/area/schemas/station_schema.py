from pydantic import BaseModel
from typing import Optional

class StationCurrentRequest(BaseModel):
    user_id: int  # ✅ `POST` で受け取る `user_id`

class LocationRequest(BaseModel):
    lat: float  # 緯度
    lon: float  # 経度

class StationResponse(BaseModel):
    id: int
    name: str
    line_name: Optional[str] = "不明"  # 路線名がない場合は「不明」
    distance_km: Optional[float] = 0.0 
    line_id: Optional[int] = None  # 必要なら追加

class StationRegisterRequest(BaseModel):
    station: int  # 最寄り駅のID
