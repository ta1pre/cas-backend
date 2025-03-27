# 📂 app/features/customer/area/repositories/station_repository.py
from sqlalchemy.orm import Session
from app.db.models.station import Station
from app.db.models.user import User

def get_user_station(db: Session, user_id: int):
    """ユーザーの最寄り駅を取得"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.station:
        return None
    return db.query(Station).filter(Station.id == user.station).first()
