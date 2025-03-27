# resv_no_show_reports.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class ResvNoShowReports(Base):
    __tablename__ = "resv_no_show_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reservation_id = Column(Integer, ForeignKey("resv_reservation.id", ondelete="CASCADE"), nullable=False)

    # 現状はユーザーのみ報告と想定
    reported_by = Column(String(20), nullable=False)  # 'user'
    reason = Column(String(255), nullable=False)

    reported_at = Column(DateTime(timezone=True), server_default=func.now())
