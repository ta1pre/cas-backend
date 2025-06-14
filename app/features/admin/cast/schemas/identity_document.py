"""Pydantic schema for Admin Cast Identity Documents"""
from datetime import datetime
from pydantic import BaseModel


class IdentityDocOut(BaseModel):
    """レスポンス用スキーマ (身分証画像)"""

    id: int
    url: str
    created_at: datetime
    status: str | None = None

    class Config:
        orm_mode = True
