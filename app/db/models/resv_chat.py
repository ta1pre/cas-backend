from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.db.session import Base  # ✅ 既存のBaseクラスを継承

class ResvChat(Base):
    __tablename__ = "resv_chat"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(Integer, ForeignKey("resv_reservation.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, nullable=False)  # ✅ ユーザー/キャスト/管理者のID
    sender_type = Column(Enum("user", "cast", "admin", name="sender_type_enum"), nullable=False)  # ✅ 送信者のタイプ
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    # ✅ 予約データとのリレーション
    reservation = relationship("ResvReservation", back_populates="chat_messages")
