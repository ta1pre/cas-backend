# app/features/reserve/change_status/hooks/change_status/confirmed/confirmed_repository.py

from sqlalchemy.orm import Session
from app.db.models.point import PointBalance  # ✅ 修正: `PointBalance` から取得
from app.db.models.resv_reservation import ResvReservation

def get_user_points(db: Session, user_id: int) -> int:
    """
    ユーザーの現在のポイント残高を取得する
    """
    point_balance = db.query(PointBalance).filter(PointBalance.user_id == user_id).first()
    return point_balance.total_point_balance if point_balance else None  # ✅ 合計ポイントを取得

def get_reservation_total(db: Session, reservation_id: int) -> int:
    """
    予約の合計金額（total_points）を取得する
    """
    reservation = db.query(ResvReservation).filter(ResvReservation.id == reservation_id).first()
    return reservation.total_points if reservation else None
