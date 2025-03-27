# app/db/models/point_details.py
from sqlalchemy import Column, Integer, ForeignKey, String, Enum, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from app.db.session import Base
from sqlalchemy.sql import func

# ✅ キャストが提供するオプション
class PointOptionMap(Base):
    __tablename__ = "pnt_option_map"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cast_id = Column(Integer, ForeignKey("cast_common_prof.cast_id"), nullable=False)
    option_id = Column(Integer, nullable=False)  # ✅ オプションID
    is_active = Column(Boolean, default=True)  # ✅ オプションの有効/無効
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    cast = relationship("CastCommonProf", back_populates="option_map",
    primaryjoin="PointOptionMap.cast_id == CastCommonProf.cast_id")

# ✅ コースのオプション
class PointDetailsOption(Base):
    __tablename__ = "pnt_details_option"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, nullable=False)
    option_name = Column(String(255), nullable=False)  # ✅ オプション名
    price = Column(Integer, nullable=False, default=0)  # ✅ オプション価格
    description = Column(String(255), nullable=True)  # ✅ オプションの説明
    created_at = Column(DateTime, server_default=func.now())

# ✅ コース詳細
class PointDetailsCourse(Base):
    __tablename__ = "pnt_details_course"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_type = Column(Integer, nullable=False)  # ✅ コース種別
    course_name = Column(String(255), nullable=False)  # ✅ コース名
    description = Column(String(255), nullable=True)  # ✅ コース説明
    duration_minutes = Column(Integer, nullable=False)  # ✅ 時間（分）
    cost_points = Column(Integer, nullable=False)  # ✅ 必要ポイント
    cast_reward_points = Column(Integer, nullable=False)  # ✅ キャスト報酬ポイント
    is_active = Column(Boolean, default=True)  # ✅ コースの有効/無効
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

