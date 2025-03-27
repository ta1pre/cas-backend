# app/features/points/repositories/points_repository.py

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from app.db.models.point import PointBalance, PointTransaction, PointRule
from datetime import datetime, timedelta
from typing import List, Tuple
from datetime import timezone

def get_point_balance(db: Session, user_id: int):
    return db.query(PointBalance).filter_by(user_id=user_id).first()

def get_transaction_history(db: Session, user_id: int, limit: int, offset: int) -> Tuple[List[PointTransaction], int]:
    """
    ✅ 指定ユーザーの過去3ヶ月以内のポイント履歴を取得する（ルール説明を含める）
    """
    three_months_ago = datetime.now(timezone.utc) - timedelta(days=90)

    # ✅ `rule_description` を `JOIN` して取得
    history_query = db.query(PointTransaction).filter(
        PointTransaction.user_id == user_id,
        PointTransaction.created_at >= three_months_ago
    ).order_by(PointTransaction.created_at.desc()).options(joinedload(PointTransaction.rule))  # ✅ `JOIN` で `rule_description` を取得

    total_count = history_query.count()  # ✅ 全件数を取得
    history = history_query.offset(offset).limit(limit).all()

    return history, total_count