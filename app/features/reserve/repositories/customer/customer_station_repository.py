from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.db.models.user import User
from app.db.models.cast_common_prof import CastCommonProf
from app.db.models.station import Station

def get_user_station(user_id: int, db: Session):
    """ユーザーの登録駅を取得"""
    stmt = select(Station).join(User, User.station == Station.id).where(User.id == user_id)
    result = db.execute(stmt).scalar_one_or_none()
    return result

def get_cast_station(cast_id: int, db: Session):
    """キャストの登録駅を取得"""
    stmt = select(Station).join(CastCommonProf, CastCommonProf.dispatch_prefecture == Station.id).where(CastCommonProf.cast_id == cast_id)
    result = db.execute(stmt).scalar_one_or_none()
    return result
