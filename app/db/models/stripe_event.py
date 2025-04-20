from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
#from sqlalchemy.orm import relationship  # 一旦不要なリレーションは外す
from app.db.session import Base
from datetime import datetime, timezone

class StripeEvent(Base):
    __tablename__ = "stripe_events"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    event_id = Column(String(64), unique=True, nullable=False, index=True, doc="StripeイベントID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, doc="処理対象ユーザーID")
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, doc="処理日時")
    transaction_id = Column(Integer, ForeignKey("pnt_point_transactions.id"), nullable=True, doc="関連ポイント取引ID")
    description = Column(String(255), nullable=True, doc="任意の説明・メモ")

    # --- リレーションは一旦外す（登録だけ確実に通すため） ---
    # user = relationship("User", backref="stripe_events")
    # transaction = relationship("PointTransaction", backref="stripe_events")

    __table_args__ = (
        UniqueConstraint("event_id", name="uq_stripe_event_id"),
    )
