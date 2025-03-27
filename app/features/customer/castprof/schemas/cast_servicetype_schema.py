# app/features/customer/castprof/schemas/cast_servicetype_schema.py

from pydantic import BaseModel
from typing import List

class ServiceTypeSchema(BaseModel):
    """キャストのサービス種別のスキーマ"""
    id: int
    name: str
    category: str
    weight: int

    class Config:
        orm_mode = True
