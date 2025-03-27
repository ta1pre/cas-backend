# app/features/customer/castprof/service/cast_traits_service.py

from sqlalchemy.orm import Session
from app.features.customer.castprof.repositories.cast_traits_repository import get_cast_traits
from app.features.customer.castprof.schemas.cast_traits_schema import TraitSchema

def fetch_cast_traits(cast_id: int, db: Session):
    """キャストの特徴一覧を取得し、Pydanticスキーマに変換"""
    traits = get_cast_traits(cast_id, db)
    return [TraitSchema(id=t.id, name=t.name, category=t.category, weight=t.weight) for t in traits]
