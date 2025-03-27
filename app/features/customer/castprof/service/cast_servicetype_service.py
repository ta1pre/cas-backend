# app/features/customer/castprof/service/cast_servicetype_service.py

from sqlalchemy.orm import Session
from app.features.customer.castprof.repositories.cast_servicetype_repository import get_cast_servicetypes
from app.features.customer.castprof.schemas.cast_servicetype_schema import ServiceTypeSchema

def fetch_cast_servicetypes(cast_id: int, db: Session):
    """キャストのサービス種別一覧を取得し、Pydanticスキーマに変換"""
    servicetypes = get_cast_servicetypes(cast_id, db)
    return [ServiceTypeSchema(id=s.id, name=s.name, category=s.category, weight=s.weight) for s in servicetypes]
