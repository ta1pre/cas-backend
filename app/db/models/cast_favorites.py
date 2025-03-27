from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.db.session import Base

class CastFavorite(Base):
    __tablename__ = "cast_favorites"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cast_id = Column(Integer, ForeignKey("cast_common_prof.cast_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 同じユーザーが同じキャストをお気に入り登録できないようにする
    __table_args__ = (
        UniqueConstraint('user_id', 'cast_id', name='unique_user_cast_favorite'),
    )
