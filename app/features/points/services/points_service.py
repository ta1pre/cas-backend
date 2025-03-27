# app/features/points/services/points_service.py

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.point import PointTransaction, PointRule
from app.features.points.repositories.points_repository import get_point_balance, get_transaction_history
from app.features.points.schemas.points_schema import PointBalanceResponse, PointHistoryResponse, PointHistoryItem

def fetch_point_balance(db: Session, user_id: int) -> PointBalanceResponse:
    user_points = get_point_balance(db, user_id)

    if not user_points:
        return PointBalanceResponse(
            user_id=user_id,
            regular_points=0,
            bonus_points=0,
            total_points=0
        )

    return PointBalanceResponse(
        user_id=user_points.user_id,
        regular_points=user_points.regular_point_balance,
        bonus_points=user_points.bonus_point_balance,
        total_points=user_points.total_point_balance
    )

def fetch_point_history(db: Session, user_id: int, limit: int, offset: int) -> PointHistoryResponse:
    """
    ✅ ポイント履歴データを取得し、レスポンス形式に変換（`rule_description` を含む）
    """
    transactions, total_count = get_transaction_history(db, user_id, limit, offset)

    history_items = [
        PointHistoryItem(
            transaction_id=t.id,
            transaction_type=t.transaction_type,
            point_change=t.point_change,
            point_source=t.point_source,
            balance_after=t.balance_after,
            created_at=t.created_at,
            rule_description=t.rule.rule_description if t.rule else "不明な取引"  # ✅ ルールの説明を含める
        )
        for t in transactions
    ]

    return PointHistoryResponse(history=history_items, total_count=total_count)