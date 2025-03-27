# app/features/notifications/handlers/reservation_canceled.py

from sqlalchemy.orm import Session
from app.features.notifications.templates import get_template
from app.features.notifications.variables import get_reservation_variables
from app.features.notifications.line import send_line_message
from app.features.notifications.repository.getlineID_repository import get_user_line_id  

def send_reservation_canceled(db: Session, reservation_id: int, user_id: int):
    """
    予約キャンセル時の通知を送る
    """
    # 1️⃣ 予約情報を取得
    variables = get_reservation_variables(db, reservation_id)

    # 2️⃣ メッセージを作成
    template = get_template("reservation_canceled")
    message = template.format(**variables)

    # 3️⃣ LINE ID を取得し、送信
    line_id = get_user_line_id(db, user_id)
    if line_id:
        send_line_message(line_id, message)
    else:
        print(f"❌ ユーザー {user_id} のLINE IDが見つかりません")
