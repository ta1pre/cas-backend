from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nick_name = Column(String(255), nullable=True)
    prefectures = Column(String(255), nullable=True)
    station = Column(Integer, ForeignKey("stations.id"), nullable=True)  # 🔄 最寄り駅を `stations.id` に変更
    line_id = Column(String(255), unique=True, nullable=False, index=True)
    invitation_id = Column(String(255), unique=True, nullable=True, index=True)
    tracking_id = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    email_verified = Column(Boolean, default=False)
    mobile_phone = Column(String(255), nullable=True)
    phone_verification_code = Column(String(6), nullable=True)
    phone_verified = Column(Boolean, default=False)
    picture_url = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    sex = Column(String(255), nullable=True)
    birth = Column(String(255), nullable=True)
    user_type = Column(String(255), nullable=True)
    affi_type = Column(Integer, nullable=True)
    last_login = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    setup_status = Column(String(50), nullable=True, default=None)
    stripe_customer_id = Column(String(255), nullable=True, unique=True)


    # ✅ `stations` テーブルとの関係を定義
    nearest_station = relationship("Station", backref="users")

    def __repr__(self):
        # __repr__ で遅延ロードを誘発しないよう、一次キーなど最小限の情報にとどめる
        # id が expire していてもセッションを介さず取得できるよう __dict__ から直接参照
        user_id = self.__dict__.get("id", None)
        return f"<User id={user_id}>"
