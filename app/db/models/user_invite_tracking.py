# app/db/models/user_invite_tracking.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.session import Base

class UserInviteTracking(Base):
    __tablename__ = "user_invite_trackings"

    id = Column(Integer, primary_key=True, autoincrement=True)

    inviter_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invited_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    display_number = Column(Integer, nullable=False)  # 紹介ユーザー①〜の表示用番号
    total_earned_point = Column(Integer, default=0)   # 累計ポイント

    created_at = Column(DateTime, server_default=func.now())

    # リレーション
    inviter_user = relationship("User", foreign_keys=[inviter_user_id], backref="invited_users")
    invited_user = relationship("User", foreign_keys=[invited_user_id], backref="invited_by")
