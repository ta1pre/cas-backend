# app/features/points/services/purchase_service.py

from sqlalchemy.orm import Session
from app.features.points.repositories.purchase_repository import (
    add_point_transaction,
    update_user_balance,
    get_user_balance
)

def process_point_purchase(db: Session, user_id: int, amount: int):
    """✅ ユーザーのポイント購入処理（履歴追加 & 残高更新）"""

    if amount < 100 or amount > 1_000_000:
        raise ValueError("🚨 購入可能なポイントは100～1,000,000です")

    add_point_transaction(db, user_id, amount)  # ✅ 取引履歴に記録
    updated_balance = update_user_balance(db, user_id, amount)  # ✅ ユーザーのポイントを更新
    
    return updated_balance
