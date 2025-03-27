#app/features/customer/castprof/repositories/castprof_repository.py

from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.db.models.cast_common_prof import CastCommonProf

def get_cast_profile(cast_id: int, db: Session):
    """キャストのプロフィールを取得"""
    stmt = select(CastCommonProf).where(CastCommonProf.cast_id == cast_id)
    result = db.execute(stmt).scalar_one_or_none()

    if not result:
        return None

    return result

