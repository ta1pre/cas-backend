# ✅ app/db/models/station_distance.py
from sqlalchemy import Column, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base
from .station import Station

class StationDistance(Base):
    __tablename__ = "station_distances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_station_id = Column(Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False)
    to_station_id = Column(Integer, ForeignKey("stations.id", ondelete="CASCADE"), nullable=False)
    distance_km = Column(Float, nullable=False)

    # ✅ ユニーク制約（同じ駅ペアを重複登録しない）
    __table_args__ = (UniqueConstraint("from_station_id", "to_station_id", name="from_to_idx"),)

    # ✅ リレーション（Station モデルと接続）
    from_station = relationship("Station", foreign_keys=[from_station_id])
    to_station = relationship("Station", foreign_keys=[to_station_id])
