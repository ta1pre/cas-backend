from sqlalchemy.orm import Session
from app.features.reserve.repositories.customer.customer_station_repository import get_user_station, get_cast_station



def get_stations(user_id: int, cast_id: int, db: Session):
    """ユーザーとキャストの登録駅を取得する"""
    user_station = get_user_station(user_id, db)
    cast_station = get_cast_station(cast_id, db)

    return {
        "user_station": {
            "station_id": user_station.id if user_station else None,
            "station_name": user_station.name if user_station else None
        },
        "cast_station": {
            "station_id": cast_station.id if cast_station else None,
            "station_name": cast_station.name if cast_station else None
        }
    }
