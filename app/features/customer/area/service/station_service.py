#app/features/customer/area/service/station_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func, literal_column
from app.db.models.station import Station
from app.db.models.line import Line
from app.db.models.user import User
from pyproj import Geod
from collections import defaultdict
from app.features.customer.area.repositories.station_repository import get_user_station
from app.features.customer.area.schemas.station_schema import StationResponse
from fastapi import HTTPException

geod = Geod(ellps="WGS84")

def calculate_distance(lat1, lon1, lat2, lon2):
    _, _, distance = geod.inv(lon1, lat1, lon2, lat2)
    return distance / 1000

def get_nearest_stations(db: Session, user_id: int, lat: float, lon: float, limit: int = 5):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}

    # ✅ 駅名ごとに全ての路線名を取得（GROUP_CONCAT使用）
    stations = (
        db.query(
            Station.name.label("station_name"),
            func.group_concat(func.distinct(Line.line_name)).label("line_names"),
            func.min(Station.id).label("station_id"),
            func.min(Station.lat).label("lat"),
            func.min(Station.lon).label("lon"),
        )
        .join(Line, Station.line_id == Line.id)
        .group_by(Station.name)
        .all()
    )

    valid_stations = []
    for s in stations:
        if s.lat and s.lon:
            distance = round(calculate_distance(lat, lon, s.lat, s.lon), 2)
            line_names = s.line_names.split(",") if s.line_names else ["不明"]

            line_name_display = line_names[0]  # 最初の路線名を表示用に使う
            if len(line_names) > 1:
                line_name_display += " (複数路線)"

            valid_stations.append({
                "id": s.station_id,
                "name": s.station_name,
                "line_name": line_name_display,
                "distance_km": distance
            })

    sorted_stations = sorted(valid_stations, key=lambda s: s["distance_km"])[:limit]

    return sorted_stations

def register_station_for_user(db: Session, user_id: int, station_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    station = db.query(Station).filter(Station.id == station_id).first()

    if not user:
        return {"error": "User not found"}
    if not station:
        return {"error": "Station not found"}

    user.station = station.id
    user.prefectures = station.pref_cd
    db.commit()

    return {"message": f"Nearest station '{station.name}' registered successfully"}

def fetch_current_station(db: Session, user_id: int):
    """現在の最寄り駅を取得するサービス"""
    station = get_user_station(db, user_id)
    if not station:
        raise HTTPException(status_code=404, detail="最寄り駅が見つかりません")
    
    return StationResponse(
        id=station.id,
        name=station.name,
        line_name=station.line.line_name if station.line else "不明",
        distance_km=0.0, 
        line_id=station.line_id
    )
