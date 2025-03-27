from pydantic import BaseModel
from typing import Literal

class MessageCreateRequest(BaseModel):
    user_id: int
    reservation_id: int
    sender_type: Literal["user", "cast", "admin"]  # ✅ sender_type を追加
    message: str

class MessageCreateResponse(BaseModel):
    message_id: int
    status: str
