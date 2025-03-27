from sqlalchemy.orm import Session
from app.db.models.resv_status_history import ResvStatusHistory

def insert_status_history(db: Session, reservation_id: int, user_id: int, prev_status: str, new_status: str, latitude: float = None, longitude: float = None):
    """
    ステータス変更履歴を記録
    """
    new_history = ResvStatusHistory(
        reservation_id=reservation_id,
        changed_by=str(user_id),
        prev_status=prev_status,
        new_status=new_status,
        latitude=latitude,
        longitude=longitude
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
