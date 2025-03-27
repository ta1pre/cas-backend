# app/features/customer/castprof/repositories/cast_traits_repository.py

from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.db.models.cast_traits import CastTrait
from app.db.models.cast_traits import CastTraitList

def get_cast_traits(cast_id: int, db: Session):
    """キャストの特徴（Traits）を取得"""
    stmt = (
        select(CastTraitList)
        .join(CastTrait, CastTraitList.id == CastTrait.trait_id)
        .where(CastTrait.cast_id == cast_id)
    )
    result = db.execute(stmt).scalars().all()
    return result
