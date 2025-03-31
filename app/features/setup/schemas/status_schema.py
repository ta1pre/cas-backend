from pydantic import BaseModel
from typing import Dict, Any, Optional

class ProfileUpdateRequest(BaseModel):
    user_id: int
    user_type: str
    cast_type: Optional[str] = None  # 'cas' または 'delicas'
    profile_data: Dict[str, Any]
