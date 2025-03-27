# ✅ app/features/insertDistances/repositories/insert_distance.py
from sqlalchemy.orm import Session
from app.db.models.station_distance import StationDistance

def insert_one_distance(db: Session, from_station_id: int, to_station_id: int, distance_km: float):
    """ station_distances に 1 行追加 """
    new_distance = StationDistance(
        from_station_id=from_station_id,
        to_station_id=to_station_id,
        distance_km=distance_km
    )
    db.add(new_distance)
    db.commit()
    db.refresh(new_distance)
    return new_distance
