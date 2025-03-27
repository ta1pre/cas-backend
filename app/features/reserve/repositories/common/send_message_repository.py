from sqlalchemy.orm import Session
from app.db.models.resv_chat import ResvChat
from app.features.reserve.schemas.common.send_message_schema import MessageCreateRequest
from sqlalchemy.exc import SQLAlchemyError

def save_message(db: Session, request: MessageCreateRequest):
    new_message = ResvChat(
        reservation_id=request.reservation_id,
        sender_id=request.user_id,
        sender_type=request.sender_type,
        message=request.message
    )

    try:
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        return {"message_id": new_message.id, "status": "sent"}
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"メッセージ送信エラー: {str(e)}")
