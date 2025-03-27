# app/features/customer/castprof/schemas/cast_traits_schema.py

from pydantic import BaseModel

class TraitSchema(BaseModel):
    """キャストの特徴のスキーマ"""
    id: int
    name: str
    category: str
    weight: int

    class Config:
        orm_mode = True
