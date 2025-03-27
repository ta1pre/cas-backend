from sqlalchemy.orm import Session
from app.db.models.resv_status_history import ResvStatusHistory
from datetime import datetime
from datetime import timezone

def save_status(db: Session, reservation_id: int, status: str, changed_by: str):
    status_history = ResvStatusHistory(
        reservation_id=reservation_id,
        prev_status="none",
        new_status=status,
        changed_by=changed_by,
    )
    db.add(status_history)
    db.commit()
