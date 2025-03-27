# app/db/models/line.py
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.db.session import Base

class Line(Base):
    __tablename__ = "lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_name = Column(String(255), nullable=False)
    lon = Column(Float, nullable=True)
    lat = Column(Float, nullable=True)
    zoom = Column(Integer, nullable=True)
    e_sort = Column(Integer, nullable=True)
    active = Column(Integer, default=1)

    # 🚨 ここが不足していたので追加
    stations = relationship("Station", back_populates="line")
