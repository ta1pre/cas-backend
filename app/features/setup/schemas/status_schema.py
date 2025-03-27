from pydantic import BaseModel
from typing import Dict, Any

class ProfileUpdateRequest(BaseModel):
    user_id: int
    user_type: str
    profile_data: Dict[str, Any]
