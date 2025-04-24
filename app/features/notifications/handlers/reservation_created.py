# app/features/notifications/handlers/reservation_created.py

from sqlalchemy.orm import Session
from app.features.notifications.templates import get_template
from app.features.notifications.variables import get_reservation_variables
from app.features.notifications.line import send_line_message
from app.features.notifications.repository.getlineID_repository import get_user_line_id
from app.db.models.resv_reservation import ResvReservation

def send_reservation_created(db: Session, reservation_id: int, user_id: int):
    """
    予約作成時の通知を送る（ユーザー・キャスト両方）
    """
    # 1️⃣ 予約情報を取得
    variables = get_reservation_variables(db, reservation_id)

    # ユーザー向け通知
    template_user = get_template("reservation_created")
    message_user = template_user.format(**variables)
    user_line_id = get_user_line_id(db, user_id)
    send_line_message(user_line_id, message_user)

    # キャスト向け通知
    template_cast = get_template("reservation_created_cast")
    message_cast = template_cast.format(**variables)
    cast_line_id = get_user_line_id(db, variables.get("cast_id")) if variables.get("cast_id") else None
    if not cast_line_id:
        # 変数にcast_idがなければreservationから取得
        reservation = db.query(ResvReservation).filter(ResvReservation.id == reservation_id).first()
        cast_line_id = get_user_line_id(db, reservation.cast_id) if reservation else None
    if cast_line_id:
        send_line_message(cast_line_id, message_cast)
