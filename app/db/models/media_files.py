# ✅ media_files.py - メディアファイル管理モデル
from sqlalchemy import Column, Integer, String, Enum, DateTime, Index
from sqlalchemy.sql import func
from app.db.session import Base

class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_url = Column(String(500), nullable=False)  # ✅ S3の画像URL
    file_type = Column(Enum('image', 'video', 'document'), nullable=False, default="image")  # ✅ ファイル種別
    target_type = Column(Enum('profile_common', 'profile_a', 'profile_b', 'blog', 'cast_identity_verification'), nullable=False)  # ✅ 用途
    target_id = Column(Integer, nullable=False)  # ✅ 紐付け先ID（キャストID・記事IDなど）
    order_index = Column(Integer, default=0)  # ✅ 表示順（0~4）
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_target_type_id", "target_type", "target_id"),  # ✅ 高速検索用インデックス
        Index("idx_order_index", "target_id", "order_index")       # ✅ 表示順制御用インデックス
    )
