# src/app/features/customer/search/repositories/user_repository.py

from sqlalchemy.orm import Session
from app.db.models.user import User

def get_user_prefecture(db: Session, user_id: int):
    """ユーザーの都道府県IDを取得"""
    user = db.query(User.prefectures).filter(User.id == user_id).first()  # ✅ `User.prefecture` → `User.prefectures` に修正
    return user.prefectures if user else None  # ✅ 修正


from app.db.models.prefectures import Prefecture
def get_prefecture_name(db: Session, prefecture_id: int) -> str | None:
    """都道府県のIDを元に都道府県名を取得する"""
    prefecture = db.query(Prefecture.name).filter(Prefecture.id == prefecture_id).scalar()
    return prefecture
