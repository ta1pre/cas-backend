# ✅ cast_prof_b.py - B種別キャスト詳細プロフィールモデル
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class CastProfB(Base):
    __tablename__ = "cast_prof_b"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cast_id = Column(Integer, ForeignKey("cast_common_prof.cast_id", ondelete="CASCADE"), nullable=False)
    free_area = Column(String(500))  # ✅ 自己紹介・PR欄
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
