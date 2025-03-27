# app/features/customer/castprof/schemas/castprof_schema.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.features.customer.castprof.schemas.image_schema import ImageData
from app.features.customer.castprof.schemas.cast_traits_schema import TraitSchema
from app.features.customer.castprof.schemas.cast_servicetype_schema import ServiceTypeSchema

class CastProfileRequest(BaseModel):
    cast_id: int
    user_id: Optional[int] = None

class CastProfileResponse(BaseModel):
    cast_id: int
    cast_type: Optional[str]
    rank_id: Optional[int]
    name: Optional[str]
    age: Optional[int]
    height: Optional[int]
    bust: Optional[int]
    cup: Optional[str]
    waist: Optional[int]
    hip: Optional[int]
    birthplace: Optional[str]
    blood_type: Optional[str]
    hobby: Optional[str]
    profile_image_url: Optional[str]
    reservation_fee: Optional[int]
    popularity: int
    rating: float
    self_introduction: Optional[str]
    job: Optional[str]
    dispatch_prefecture: Optional[str]
    support_area: Optional[str]
    is_active: Optional[int]
    available_at: Optional[datetime]
    images: List[ImageData]  # ✅ 画像をリストで追加
    traits: List[TraitSchema] = []  # ✅ キャストの特徴を追加
    service_types: List[ServiceTypeSchema] = []  # ✅ キャストのサービス種別を追加

    class Config:
        from_attributes = True
