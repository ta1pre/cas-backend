# app/features/notifications/handlers/reservation_confirmed.py

from sqlalchemy.orm import Session
from app.features.notifications.templates import get_template
from app.features.notifications.variables import get_reservation_variables
from app.features.notifications.line import send_line_message
from app.features.notifications.repository.getlineID_repository import get_user_line_id

def send_reservation_confirmed(db: Session, reservation_id: int, user_id: int):
    """
    予約確定時の通知を送る
    """
    # 1️⃣ 予約情報を取得
    variables = get_reservation_variables(db, reservation_id)
    if not variables:
        print(f"❌ 予約ID {reservation_id} の情報取得に失敗")
        return

    # 2️⃣ メッセージを作成
    template = get_template("reservation_confirmed") # キーを confirmed に変更
    message = template.format(**variables)

    # 3️⃣ LINE ID を取得し、送信
    line_id = get_user_line_id(db, user_id)
    if line_id:
        send_line_message(line_id, message)
    else:
        print(f"❌ ユーザー {user_id} のLINE IDが見つかりません")
