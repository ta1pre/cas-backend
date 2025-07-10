# app/features/points/services/points_service.py

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.point import PointTransaction, PointRule
from app.features.points.repositories.points_repository import (
    get_point_balance,
    get_transaction_history,
    get_point_balance_by_user_id,
    create_initial_point_balance,
    update_point_balance,
    record_point_transaction,
    get_point_rule_by_event_type_and_target,
    get_referred_users_by_referrer_invitation_id
)
from app.features.points.schemas.points_schema import PointBalanceResponse, PointHistoryResponse, PointHistoryItem
from typing import Optional, Dict, Any, List # Listを追加
from app.db.models.user import User # Userモデルを先頭に移動

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
        pending_points=user_points.pending_point_balance,
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

def adjust_pending_points(
    db: Session,
    user_id: int,
    amount: int,
    point_source: str, # 'regular', 'bonus', 'pending'
    description: Optional[str] = None,
    rule_id: Optional[int] = None,
    related_id: Optional[int] = None,
    related_table: Optional[str] = None
) -> PointBalanceResponse:
    """
    仮ポイント残高を調整し、取引履歴を記録する
    """
    updated_balance = update_point_balance(
        db, user_id, pending_change=amount
    )

    record_point_transaction(
        db,
        user_id,
        transaction_type="referral_bonus_pending", # 仮ポイント付与のタイプ
        point_change=amount,
        point_source=point_source,
        balance_after=updated_balance.total_point_balance,
        description=description,
        rule_id=rule_id,
        related_id=related_id,
        related_table=related_table
    )
    return PointBalanceResponse.from_orm(updated_balance)

def confirm_pending_points(
    db: Session,
    user_id: int,
    amount: int,
    point_source: str, # 'regular', 'bonus'
    description: Optional[str] = None,
    rule_id: Optional[int] = None,
    related_id: Optional[int] = None,
    related_table: Optional[str] = None
) -> PointBalanceResponse:
    """
    仮ポイントを確定ポイントに変換し、取引履歴を記録する
    """
    # 仮ポイントを減らし、確定ポイントを増やす
    regular_change = amount if point_source == "regular" else 0
    bonus_change = amount if point_source == "bonus" else 0

    updated_balance = update_point_balance(
        db, user_id,
        regular_change=regular_change,
        bonus_change=bonus_change,
        pending_change=-amount # 仮ポイントを減らす
    )

    record_point_transaction(
        db,
        user_id,
        transaction_type="referral_bonus_completed", # 仮ポイント確定のタイプ
        point_change=amount,
        point_source=point_source,
        balance_after=updated_balance.total_point_balance,
        description=description,
        rule_id=rule_id,
        related_id=related_id,
        related_table=related_table
    )
    return PointBalanceResponse.from_orm(updated_balance)

def process_point_event(db: Session, event_type: str, event_data: Dict[str, Any]):
    """
    ポイント関連のイベントを処理し、適切なポイントルールを適用する
    """
    # イベントタイプに基づいてルールを検索
    # 紹介者へのルール
    referrer_rule = get_point_rule_by_event_type_and_target(db, event_type, 'referrer')
    # 被紹介者へのルール (必要であれば)
    referred_rule = get_point_rule_by_event_type_and_target(db, event_type, 'referred')

    # イベントデータから必要な情報を抽出
    referred_user_id = event_data.get('referred_user_id')
    referred_user_tracking_id = event_data.get('tracking_id')
    attended_user_id = event_data.get('attended_user_id') # 出勤イベント用

    # 紹介者（referrer）の特定
    referrer_user: Optional[User] = None
    if referred_user_tracking_id:
        # tracking_idを持つユーザー（被紹介者）のinvitation_idが紹介者のinvitation_id
        # ここでは、tracking_idが紹介者のinvitation_idと一致すると仮定
        # 実際には、tracking_idから紹介者を特定するロジックが必要
        # 例: AccountRepository.get_user_by_invitation_id(referred_user_tracking_id)
        # 現状、points_repositoryにはUserモデルを直接扱う関数がないため、AccountRepositoryから取得する
        # ここでは簡略化のため、直接Userモデルをクエリする
        referrer_user = db.query(User).filter(User.invitation_id == referred_user_tracking_id).first()

    # --- user_registered_by_referral イベント処理 ---
    if event_type == 'user_registered_by_referral':
        if referrer_user and referrer_rule:
            # 紹介者への仮ポイント付与
            adjust_pending_points(
                db,
                user_id=referrer_user.id,
                amount=int(referrer_rule.point_value),
                point_source=referrer_rule.point_type,
                description=f"{referrer_rule.rule_name} (紹介者)",
                rule_id=referrer_rule.id,
                related_id=referred_user_id,
                related_table="user"
            )
        # 被紹介者へのポイント付与 (もしあれば)
        if referred_user_id and referred_rule:
            # ここでは被紹介者へのポイントは確定ポイントとして付与すると仮定
            # 必要に応じてadjust_pending_pointsを使う
            # 例: adjust_points_manual(db, referred_user_id, int(referred_rule.point_value), referred_rule.point_type, f"{referred_rule.rule_name} (被紹介者)", referred_rule.id)
            pass # 今回は被紹介者へのポイント付与はスコープ外

    # --- referred_user_first_attendance イベント処理 ---
    elif event_type == 'referred_user_first_attendance':
        if attended_user_id:
            # 出勤したユーザー（被紹介者）のtracking_idを取得
            attended_user = db.query(User).filter(User.id == attended_user_id).first()
            if attended_user and attended_user.tracking_id:
                # 被紹介者のtracking_idから紹介者を特定
                referrer_user_for_attendance = db.query(User).filter(User.invitation_id == attended_user.tracking_id).first()
                if referrer_user_for_attendance and referrer_rule:
                    # 紹介者への仮ポイント確定
                    confirm_pending_points(
                        db,
                        user_id=referrer_user_for_attendance.id,
                        amount=int(referrer_rule.point_value), # 仮ポイント付与時と同じポイント数
                        point_source=referrer_rule.point_type,
                        description=f"{referrer_rule.rule_name} (紹介ポイント確定)",
                        rule_id=referrer_rule.id,
                        related_id=attended_user_id,
                        related_table="user"
                    )

def get_referred_users_list(db: Session, referrer_user_id: int) -> List[User]:
    """
    紹介者が紹介したユーザー（被紹介者）の一覧を取得する
    """
    # 紹介者のinvitation_idを取得
    referrer = db.query(User).filter(User.id == referrer_user_id).first()
    if not referrer or not referrer.invitation_id:
        return [] # 紹介者が見つからないか、invitation_idがない場合は空リストを返す

    # そのinvitation_idをtracking_idとして持つユーザーを検索
    referred_users = get_referred_users_by_referrer_invitation_id(db, referrer.invitation_id)
    return referred_users