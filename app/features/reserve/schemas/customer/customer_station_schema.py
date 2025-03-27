from pydantic import BaseModel
from typing import Optional

class StationData(BaseModel):
    station_id: Optional[int]
    station_name: Optional[str]

class CustomerStationRequest(BaseModel):
    user_id: int
    cast_id: int

class CustomerStationResponse(BaseModel):
    user_station: StationData
    cast_station: StationData
