# app/features/notifications/repository/getlineID_repository.py

from sqlalchemy.orm import Session
from app.db.models.user import User  # ✅ ユーザーモデルをインポート

def get_user_line_id(db: Session, user_id: int) -> str:
    """
    ユーザーIDからLINEのユーザーIDを取得する
    """
    user = db.query(User).filter(User.id == user_id).first()
    return user.line_id if user and user.line_id else None
