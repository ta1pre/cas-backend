# ✅ app/db/models/prefectures.py - 都道府県モデル
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.session import Base

class Prefecture(Base):
    __tablename__ = "prefectures"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(255), nullable=False, unique=True)  # ✅ 都道府県名（ユニーク制約）

    # ✅ Stationとのリレーションを正しく指定
    stations = relationship("Station", back_populates="prefecture")
