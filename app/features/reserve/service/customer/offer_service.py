from sqlalchemy.orm import Session
from app.features.reserve.schemas.customer.offer_schema import OfferReservationCreate, OfferReservationResponse
from app.features.reserve.repositories.customer.offer_repository import save_reservation
from app.features.reserve.repositories.customer.offer_status_repository import save_status
from app.features.reserve.repositories.customer.offer_chat_repository import save_chat
from datetime import datetime
import dateutil.parser
from datetime import timezone

def create_reservation(db: Session, data: OfferReservationCreate) -> OfferReservationResponse:
    """
    予約を作成する処理。
    
    `fast` の場合は、現在時刻を `start_time` に設定する。
    `custom` の場合は、受け取った `date` と `time` を組み合わせて `start_time` を作成する。
    """

    if data.timeOption == "fast":
        # ✅ `fast` の場合は NOW() を `start_time` に設定
        start_time = datetime.now(timezone.utc)
    else:
        # ✅ `custom` の場合、`date` を `datetime` に変換し、`time` を適用
        base_dt = dateutil.parser.parse(data.date)  # "YYYY-MM-DDTHH:MM:SS.sssZ" → datetime
        hour_str, minute_str = data.time.split(":")  # "HH:MM" → 時, 分を抽出
        start_time = base_dt.replace(hour=int(hour_str), minute=int(minute_str))

    # ✅ 予約を保存
    reservation = save_reservation(db, data, start_time)

    # ✅ ステータス履歴を記録
    save_status(db, reservation.id, "requested", "user")

    # ✅ メッセージがあればチャットに保存
    if data.message.strip():
        save_chat(db, reservation.id, data.userId, "user", data.message)

    return OfferReservationResponse(reservation_id=reservation.id, status="requested")
