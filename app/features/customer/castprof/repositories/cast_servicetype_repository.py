# app/features/customer/castprof/repositories/cast_servicetype_repository.py

from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.db.models.cast_servicetype import CastServiceType
from app.db.models.cast_servicetype import CastServiceTypeList

def get_cast_servicetypes(cast_id: int, db: Session):
    """キャストのサービス種別（ServiceTypes）を取得"""
    stmt = (
        select(CastServiceTypeList)
        .join(CastServiceType, CastServiceTypeList.id == CastServiceType.servicetype_id)
        .where(CastServiceType.cast_id == cast_id)
    )
    result = db.execute(stmt).scalars().all()
    return result
