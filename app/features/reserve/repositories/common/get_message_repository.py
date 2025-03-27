from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.resv_chat import ResvChat

def fetch_db_messages(db: Session, user_id: int, reservation_id: int):
    stmt = (
        select(
            ResvChat.id.label("message_id"),
            ResvChat.sender_id.label("sender_id"),  # ✅ 修正: `sender` → `sender_id`
            ResvChat.sender_type.label("sender_type"),  # ✅ 追加: `sender_type` も取得
            ResvChat.message.label("content"),
            ResvChat.created_at.label("sent_at")
        )
        .where(ResvChat.reservation_id == reservation_id)
        .order_by(ResvChat.created_at.asc())
    )

    messages = db.execute(stmt).mappings().all()

    if not messages:
        return {"messages": []}

    return {"messages": messages}
