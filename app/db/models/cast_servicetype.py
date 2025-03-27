from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.models.cast_common_prof import CastCommonProf  # ✅ 明示的に `cast_common_prof` をインポート

class CastServiceTypeList(Base):
    __tablename__ = "cast_servicetype_list"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    category = Column(String(50), nullable=False, default="その他")
    weight = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<CastServiceTypeList(id={self.id}, name={self.name}, category={self.category}, weight={self.weight}, description={self.description})>"

class CastServiceType(Base):
    __tablename__ = "cast_servicetype"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    cast_id = Column(Integer, ForeignKey(CastCommonProf.cast_id, ondelete="CASCADE"), nullable=False, index=True)  # ✅ 修正
    servicetype_id = Column(Integer, ForeignKey("cast_servicetype_list.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    servicetype = relationship("CastServiceTypeList")  # ✅ サービスタイプリストとのリレーション
    cast = relationship("CastCommonProf")  # ✅ `cast_common_prof` とのリレーションを追加

    def __repr__(self):
        return f"<CastServiceType(id={self.id}, cast_id={self.cast_id}, servicetype_id={self.servicetype_id})>"
