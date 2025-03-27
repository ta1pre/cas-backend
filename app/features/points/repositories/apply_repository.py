# app/features/points/repositories/apply_repository.py

from sqlalchemy.orm import Session
from app.db.models.point import PointBalance

def update_user_balance(db: Session, user_id: int, regular_points: int, bonus_points: int):
    """✅ ユーザーのポイント残高を更新"""
    user_balance = db.query(PointBalance).filter(PointBalance.user_id == user_id).first()

    if not user_balance:
        raise ValueError("🚨 ユーザーのポイント残高が見つかりません")

    user_balance.regular_point_balance += regular_points
    user_balance.bonus_point_balance += bonus_points
    user_balance.total_point_balance = user_balance.regular_point_balance + user_balance.bonus_point_balance  # ✅ 合計更新
    db.commit()
    return user_balance
