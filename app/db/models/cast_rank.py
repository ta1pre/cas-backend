from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.session import Base
from datetime import datetime, timedelta, timezone

def jst_now():
    return datetime.now(timezone(timedelta(hours=9)))

class CastRank(Base):
    __tablename__ = "cast_rank"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rank_name = Column(String(255), unique=True, nullable=False)  # ✅ ランク名（ユニーク）
    base_fee = Column(Integer, default=0)  # ✅ ベース料金
    description = Column(Text, nullable=True)  # ✅ ランク説明
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # ✅ 作成日時
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # ✅ 更新日時

    def __repr__(self):
        return f"<CastRank(id={self.id}, rank_name='{self.rank_name}', base_fee={self.base_fee})>"
