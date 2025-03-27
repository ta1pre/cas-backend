from sqlalchemy.orm import Session
from app.db.models.resv_chat import ResvChat
from datetime import timezone
from datetime import datetime

def save_chat(db: Session, reservation_id: int, sender_id: int, sender_type: str, message: str):
    chat = ResvChat(
        reservation_id=reservation_id,
        sender_id=sender_id,
        sender_type=sender_type,
        message=message
    )
    db.add(chat)
    db.commit()
