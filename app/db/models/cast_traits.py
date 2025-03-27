from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.session import Base
from datetime import datetime, timedelta, timezone

def jst_now():
    return datetime.now(timezone(timedelta(hours=9)))

class CastTraitList(Base):
    __tablename__ = "cast_traits_list"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    category = Column(String(50), nullable=False, default="その他")  # ✅ カテゴリを追加
    weight = Column(Integer, nullable=False, default=0)  # ✅ 並び順を管理
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<CastTraitList(id={self.id}, name={self.name}, category={self.category}, weight={self.weight})>"


class CastTrait(Base):
    __tablename__ = "cast_traits"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    cast_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False)  # ✅ `PRIMARY KEY` に変更
    trait_id = Column(Integer, ForeignKey("cast_traits_list.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=jst_now)

    trait = relationship("CastTraitList")  # ✅ 外部キーのリレーション

    def __repr__(self):
        return f"<CastTrait(id={self.id}, cast_id={self.cast_id}, trait_id={self.trait_id})>"
