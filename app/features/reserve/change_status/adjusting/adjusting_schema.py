from pydantic import BaseModel, Field
from typing import Optional

class AdjustingRequest(BaseModel):
    reservation_id: int
    user_id: int

