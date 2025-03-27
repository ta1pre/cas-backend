from pydantic import BaseModel
from typing import List

class ServiceTypeResponse(BaseModel):
    id: int
    name: str
    weight: int
    category: str  
    is_active: int  
    description: str

class SelectedServiceTypeRequest(BaseModel):
    cast_id: int  

class ServiceTypeRegisterRequest(BaseModel):
    cast_id: int
    service_type_ids: List[int]
