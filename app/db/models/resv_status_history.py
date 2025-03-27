# resv_status_history.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL
from sqlalchemy.sql import func
from app.db.session import Base

class ResvStatusHistory(Base):
    __tablename__ = "resv_status_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reservation_id = Column(Integer, ForeignKey("resv_reservation.id", ondelete="CASCADE"), nullable=False)

    changed_by = Column(String(20), nullable=False)  # 'user' / 'cast' / 'system'
    prev_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)

    status_time = Column(DateTime(timezone=True), server_default=func.now())

    # 到着時などGPSを記録したい場合のみ使用
    latitude = Column(DECIMAL(9, 6), nullable=True)
    longitude = Column(DECIMAL(9, 6), nullable=True)
