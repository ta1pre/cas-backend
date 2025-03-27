from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union

from ..schemas.station_schema import (
    LocationRequest, 
    StationResponse, 
    StationRegisterRequest, 
    StationCurrentRequest
)
from ..service.station_service import (
    get_nearest_stations, 
    register_station_for_user, 
    fetch_current_station
)
from app.db.session import get_db
from app.core.security import get_current_user
from app.db.models.user import User

router = APIRouter()

@router.post("/station/nearest", response_model=List[StationResponse])
def nearest_stations(
    request: LocationRequest, 
    db: Session = Depends(get_db), 
    user: Union[User, int] = Depends(get_current_user)
):
    """現在地から近い駅を取得"""
    # userがオブジェクト or int で受け取り可能にしつつ、確実にIDを取り出す
    user_id = user.id if isinstance(user, User) else user

    return get_nearest_stations(db, user_id, request.lat, request.lon)


@router.post("/station/register")
def register_nearest_station(
    request: StationRegisterRequest, 
    db: Session = Depends(get_db), 
    user: Union[User, int] = Depends(get_current_user)
):
    """最寄り駅を登録"""
    user_id = user.id if isinstance(user, User) else user

    return register_station_for_user(db, user_id, request.station)


@router.post("/station/current", response_model=StationResponse)
def get_current_station(
    request: StationCurrentRequest, 
    db: Session = Depends(get_db)
):
    """現在の最寄り駅を取得（POST）"""
    station = fetch_current_station(db, request.user_id)
    if not station:
        raise HTTPException(status_code=404, detail="最寄り駅が見つかりません")
    return station
