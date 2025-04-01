# app/db/models/posts.py
from sqlalchemy import Column, BigInteger, String, Text, DateTime, Enum, Integer, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # キャストID：cast_common_prof.cast_id を参照する外部キーに変更
    cast_id = Column(Integer, ForeignKey("cast_common_prof.cast_id"), nullable=False, index=True)

    # 投稿画像のURL（任意）
    photo_url = Column(String(255), nullable=True)

    # 投稿本文（必須）
    body = Column(Text, nullable=False)

    # 投稿日時：自動設定（インデックスなし）
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    # 更新日時：自動更新
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    # 公開ステータス（公開 / 非公開 / 下書き）
    status = Column(Enum("public", "private", "draft", name="poststatus"), default="public")

    # 論理削除用の削除日時
    deleted_at = Column(DateTime, nullable=True)

    # いいね数（初期値 0）
    likes_count = Column(Integer, default=0)
