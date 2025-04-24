# app/features/notifications/variables.py

from sqlalchemy.orm import Session
from app.db.models.resv_reservation import ResvReservation
from app.db.models.user import User
from app.db.models.cast_common_prof import CastCommonProf

def get_reservation_variables(db: Session, reservation_id: int) -> dict:
    """
    予約IDからDBの情報を取得し、テンプレートに渡す変数を作成
    """
    reservation = db.query(ResvReservation).filter(ResvReservation.id == reservation_id).first()

    if not reservation:
        print(f"❌ 予約ID {reservation_id} のデータが見つかりません")
        return {"location": "不明", "date": "不明", "time": "不明", "reservation_id": str(reservation_id), "cast_name": "不明", "user_name": "不明", "cast_id": None}

    # キャスト名をcast_common_profテーブルから取得
    cast_prof = db.query(CastCommonProf).filter(CastCommonProf.cast_id == reservation.cast_id).first()
    cast_name = cast_prof.name if cast_prof and cast_prof.name else "不明"

    user = db.query(User).filter(User.id == reservation.user_id).first()
    user_name = user.nick_name if user and user.nick_name else "不明"

    return {
        "location": reservation.location,
        "date": reservation.start_time.strftime("%Y-%m-%d"),
        "time": reservation.start_time.strftime("%H:%M"),
        "reservation_id": str(reservation_id),
        "cast_name": cast_name,
        "user_name": user_name,
        "cast_id": reservation.cast_id,
    }
