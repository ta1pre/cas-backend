# app/features/customer/favorites/schemas/favorites_schema.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.features.customer.castprof.schemas.image_schema import ImageData

class FavoriteBase(BaseModel):
    user_id: int
    cast_id: int

class FavoriteCreate(FavoriteBase):
    pass

class CastInfo(BaseModel):
    name: Optional[str] = None
    profile_image_url: Optional[str] = None
    age: Optional[int] = None
    images: List[ImageData] = []

class FavoriteResponse(FavoriteBase):
    id: int
    created_at: datetime
    cast_info: Optional[CastInfo] = None

    class Config:
        from_attributes = True
        orm_mode = True

class FavoriteList(BaseModel):
    favorites: List[FavoriteResponse]
