# app/features/points/repositories/points_repository.py

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from sqlalchemy import func, desc
from app.db.models.point import PointBalance, PointTransaction, PointRule
from app.db.models.user import User # Userモデルをインポート
from datetime import datetime, timedelta, timezone
from typing import List, Tuple, Optional

def get_point_balance_by_user_id(db: Session, user_id: int) -> Optional[PointBalance]:
    """
    ユーザーIDに基づいてポイント残高を取得する
    """
    return db.query(PointBalance).filter(PointBalance.user_id == user_id).first()

def create_initial_point_balance(db: Session, user_id: int) -> PointBalance:
    """
    新しいユーザーの初期ポイント残高を作成する
    """
    initial_balance = PointBalance(user_id=user_id, regular_point_balance=0, bonus_point_balance=0, pending_point_balance=0, total_point_balance=0)
    db.add(initial_balance)
    db.commit()
    db.refresh(initial_balance)
    return initial_balance

def update_point_balance(db: Session, user_id: int, regular_change: int = 0, bonus_change: int = 0, pending_change: int = 0) -> PointBalance:
    """
    ユーザーのポイント残高を更新する
    """
    balance = get_point_balance_by_user_id(db, user_id)
    if not balance:
        balance = create_initial_point_balance(db, user_id)
    
    balance.regular_point_balance += regular_change
    balance.bonus_point_balance += bonus_change
    balance.pending_point_balance += pending_change
    balance.total_point_balance = balance.regular_point_balance + balance.bonus_point_balance + balance.pending_point_balance
    
    db.commit()
    db.refresh(balance)
    return balance

def record_point_transaction(
    db: Session,
    user_id: int,
    transaction_type: str,
    point_change: int,
    point_source: str,
    balance_after: int,
    description: Optional[str] = None,
    rule_id: Optional[int] = None,
    related_id: Optional[int] = None,
    related_table: Optional[str] = None
) -> PointTransaction:
    """
    ポイント取引履歴を記録する
    """
    transaction = PointTransaction(
        user_id=user_id,
        rule_id=rule_id,
        related_id=related_id,
        related_table=related_table,
        transaction_type=transaction_type,
        point_change=point_change,
        point_source=point_source,
        balance_after=balance_after,
        description=description
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

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

def get_referred_users_by_referrer_invitation_id(db: Session, invitation_id: str) -> List[User]:
    """
    特定の招待IDで紹介されたユーザー（被紹介者）のリストを取得する
    """
    return db.query(User).filter(User.tracking_id == invitation_id).all()

def get_point_rule_by_event_type_and_target(db: Session, event_type: str, target_user_type: str) -> Optional[PointRule]:
    """
    イベントタイプとターゲットユーザータイプに基づいてポイントルールを取得する
    """
    return db.query(PointRule).filter(
        PointRule.event_type == event_type,
        PointRule.target_user_type == target_user_type
    ).first()