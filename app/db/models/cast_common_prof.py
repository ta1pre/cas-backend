from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.db.session import Base
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import relationship


def jst_now():
    return datetime.now(timezone(timedelta(hours=9)))

class CastCommonProf(Base):
    __tablename__ = "cast_common_prof"

    cast_id = Column(Integer, primary_key=True, nullable=False)  # cast_id は必須
    cast_type = Column(Enum('A', 'B', 'AB', create_constraint=True), nullable=True, default=None)  # ENUM 変更
    rank_id = Column(Integer, ForeignKey("cast_rank.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    bust = Column(Integer, nullable=True)
    cup = Column(String(255), nullable=True)
    waist = Column(Integer, nullable=True)
    hip = Column(Integer, nullable=True)
    birthplace = Column(String(255), nullable=True)
    blood_type = Column(String(255), nullable=True)
    hobby = Column(String(255), nullable=True)
    profile_image_url = Column(String(255), nullable=True)
    reservation_fee = Column(Integer, nullable=True)
    reservation_fee_deli = Column(Integer, nullable=True)
    popularity = Column(Integer, default=0, nullable=False) 
    rating = Column(Float, default=0, nullable=False) 
    self_introduction = Column(String(255), nullable=True)
    job = Column(String(255), nullable=True)
    dispatch_prefecture = Column(String(255), nullable=True)
    support_area = Column(String(255), nullable=True)
    is_active = Column(Integer, default=0, nullable=True)
    available_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)
    
    option_map = relationship("PointOptionMap", back_populates="cast")
