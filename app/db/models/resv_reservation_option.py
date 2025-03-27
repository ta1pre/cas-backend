from sqlalchemy import Column, Integer, ForeignKey, String, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.models.resv_reservation import ResvReservation
from app.db.models.point_details import PointDetailsOption

class ResvReservationOption(Base):
    __tablename__ = "resv_reservation_option"

    reservation_id = Column(Integer, ForeignKey("resv_reservation.id", ondelete="CASCADE"), primary_key=True)
    option_id = Column(Integer, ForeignKey("pnt_details_option.id", ondelete="CASCADE"), primary_key=True)
    option_price = Column(Integer, nullable=False)

    # ✅ カスタムオプション名（NULL可）
    custom_name = Column(String(255), nullable=True)

    # ✅ 状態管理カラム（デフォルトは active）
    status = Column(Enum("active", "removed"), nullable=False, default="active")

    reservation = relationship("ResvReservation", back_populates="reservation_options")

    # ✅ `back_populates` を削除し、一方向のリレーションにする
    option = relationship("PointDetailsOption")
