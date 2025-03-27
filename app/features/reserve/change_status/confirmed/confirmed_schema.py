# app/features/reserve/change_status/hooks/change_status/confirmed/confirmed_schema.py

from pydantic import BaseModel

class ConfirmedRequest(BaseModel):
    """
    予約確定時のリクエストスキーマ
    """
    user_id: int
    reservation_id: int
