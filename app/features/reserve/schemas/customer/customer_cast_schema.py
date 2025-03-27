# app/features/reserve/schemas/customer_cast_schema.py
from pydantic import BaseModel
from typing import Optional

class CustomerCastRequest(BaseModel):
    cast_id: int

class CustomerCastResponse(BaseModel):
    cast_id: int
    name: Optional[str]
    profile_image_url: Optional[str]

    class Config:
        from_attributes = True
