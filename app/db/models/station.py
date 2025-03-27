# ✅ app/db/models/station.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from .line import Line
from .prefectures import Prefecture  # ✅ Prefectureを正しくインポート

class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    line_id = Column(Integer, ForeignKey("lines.id"), nullable=True)
    pref_cd = Column(Integer, ForeignKey("prefectures.id"), nullable=True)  # ✅ 都道府県との外部キー
    lon = Column(Float, nullable=True)
    lat = Column(Float, nullable=True)
    weight = Column(Integer, default=0)
    e_sort = Column(Integer, nullable=True)

    # ✅ 都道府県とのリレーションを修正
    prefecture = relationship("Prefecture", back_populates="stations")

    # ✅ Line とのリレーション
    line = relationship("Line", back_populates="stations")
