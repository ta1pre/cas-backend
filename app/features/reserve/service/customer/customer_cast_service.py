# app/features/reserve/services/customer/customer_cast_service.py
from sqlalchemy.orm import Session
from app.features.reserve.repositories.customer.customer_cast_repository import get_customer_cast_profile
from app.features.reserve.schemas.customer.customer_cast_schema import CustomerCastResponse

def get_customer_cast_info(cast_id: int, db: Session) -> CustomerCastResponse:
    """キャスト情報を取得してレスポンスを返す"""
    cast_data = get_customer_cast_profile(cast_id, db)
    if not cast_data:
        return None
    return CustomerCastResponse(**cast_data)
