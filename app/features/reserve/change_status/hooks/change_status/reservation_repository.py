from sqlalchemy.orm import Session
from app.db.models.resv_reservation import ResvReservation

def get_current_status(db: Session, reservation_id: int) -> str:
    """
    予約テーブルから現在のステータスを取得
    """
    reservation = db.query(ResvReservation).filter(ResvReservation.id == reservation_id).first()
    return reservation.status if reservation else "unknown"

def update_reservation_status(db: Session, reservation_id: int, new_status: str, latitude: float = None, longitude: float = None):
    """
    予約のステータスを更新
    """
    reservation = db.query(ResvReservation).filter(ResvReservation.id == reservation_id).first()
    if reservation:
        reservation.status = new_status
        if latitude is not None and longitude is not None:
            reservation.latitude = latitude
            reservation.longitude = longitude
        db.commit()
