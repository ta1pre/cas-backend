# app/features/points/repositories/purchase_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.point import PointBalance, PointTransaction

def add_point_transaction(db: Session, user_id: int, amount: int):
    """✅ 購入時のポイント取引履歴を追加"""
    new_transaction = PointTransaction(
        user_id=user_id,
        rule_id=2,  # ✅ 直接購入なのでルールなし
        related_id=None,  # ✅ 関連なし
        related_table="purchase",
        transaction_type="purchase",
        point_change=amount,
        point_source="regular",
        balance_after=get_user_balance(db, user_id) + amount  # ✅ 取引後の残高
    )
    db.add(new_transaction)
    db.commit()
    return new_transaction

def update_user_balance(db: Session, user_id: int, amount: int):
    """✅ ユーザーのポイント残高を更新"""
    stmt = select(PointBalance).where(PointBalance.user_id == user_id)
    user_balance = db.execute(stmt).scalar_one_or_none()

    if not user_balance:
        raise ValueError("🚨 ユーザーのポイント残高が見つかりません")

    user_balance.regular_point_balance += amount
    user_balance.total_point_balance = (
        user_balance.regular_point_balance + user_balance.bonus_point_balance
    )  # ✅ 合計を更新
    db.commit()
    return user_balance

def get_user_balance(db: Session, user_id: int):
    """✅ ユーザーの現在のポイント残高を取得"""
    stmt = select(PointBalance.total_point_balance).where(PointBalance.user_id == user_id)
    balance = db.execute(stmt).scalar_one_or_none()
    return balance if balance is not None else 0
