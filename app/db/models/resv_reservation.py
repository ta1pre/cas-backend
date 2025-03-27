# 📂 app/db/models/resv_reservation.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, DECIMAL
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.orm import relationship

STATUS_CHOICES = (
    "requested",
    "adjusted",
    "confirmed",
    "arrived",
    "in_progress",
    "completed",
    "canceled_user",
    "canceled_cast"
)

class ResvReservation(Base):
    __tablename__ = "resv_reservation"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cast_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("pnt_details_course.id", ondelete="CASCADE"), nullable=False)

    course_points = Column(Integer, nullable=False)
    option_points = Column(Integer, nullable=False, default=0)
    reservation_fee = Column(Integer, nullable=False, default=0)
    traffic_fee = Column(Integer, nullable=False, default=0)
    total_points = Column(Integer, nullable=False)
    cast_reward_points = Column(Integer, nullable=False)

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    location = Column(String(255), nullable=False)
    latitude = Column(DECIMAL(9, 6), nullable=True)   # 施術場所の緯度
    longitude = Column(DECIMAL(9, 6), nullable=True)  # 施術場所の経度

    # 文字列Enumとして定義
    status = Column(String(50), nullable=False, default="requested")

    cancel_reason = Column(String(255), nullable=True, default=None)

    # ✅ キャスト専用メモ・施術内容のメモ欄（自由入力）
    reservation_note = Column(String(1000), nullable=True, default=None)

    is_reminder_sent = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ✅ 予約に紐づくチャットメッセージを取得可能にする
    chat_messages = relationship("ResvChat", back_populates="reservation", cascade="all, delete-orphan")
    
    # ✅ 予約に紐づくオプション情報を取得可能にする
    reservation_options = relationship("ResvReservationOption", back_populates="reservation", cascade="all, delete-orphan")
