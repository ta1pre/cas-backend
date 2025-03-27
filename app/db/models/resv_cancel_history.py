# resv_cancel_history.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class ResvCancelHistory(Base):
    __tablename__ = "resv_cancel_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reservation_id = Column(Integer, ForeignKey("resv_reservation.id", ondelete="CASCADE"), nullable=False)

    canceled_by = Column(String(20), nullable=False)  # 'user' / 'cast' / 'system'
    cancel_reason = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
