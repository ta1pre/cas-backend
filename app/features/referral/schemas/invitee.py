from pydantic import BaseModel
from datetime import datetime

class Invitee(BaseModel):
    display_number: int
    total_earned_point: int
    created_at: str  # YYYY-MM-DD 形式で返すためstr

    class Config:
        orm_mode = True
