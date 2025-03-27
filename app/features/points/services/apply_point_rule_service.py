from sqlalchemy.orm import Session
from app.db.models.point import PointTransaction, PointBalance, PointRule
from datetime import datetime, timezone, timedelta

def apply_point_rule(db: Session, user_id: int, rule_name: str, variables: dict = None):
    """ ルールを適用してポイントを更新する """

    # ✅ ルール取得
    rule = db.query(PointRule).filter(PointRule.rule_name == rule_name).first()
    if not rule:
        return {"error": f"🚨 ルール `{rule_name}` が見つかりません"}

    # ✅ ユーザーのポイント残高取得（なければ新規作成）
    balance = db.query(PointBalance).filter(PointBalance.user_id == user_id).first()
    if not balance:
        balance = PointBalance(user_id=user_id, regular_point_balance=0, bonus_point_balance=0, total_point_balance=0)
        db.add(balance)

    # ✅ ルールがボーナス or レギュラーポイントか確認
    if rule.point_type == "regular":
        balance.regular_point_balance += rule.point_value
    else:
        balance.bonus_point_balance += rule.point_value

    # ✅ 合計ポイント更新
    balance.total_point_balance += rule.point_value
    balance.last_updated = datetime.now(timezone.utc)  # ✅ `last_updated` は UTC のままでもOK

    # ✅ 取引履歴を追加（created_at を指定しない）
    transaction = PointTransaction(
        user_id=user_id,
        rule_id=rule.id,
        transaction_type=rule.transaction_type,
        point_change=rule.point_value,
        point_source=rule.point_type,  # ✅ `regular` or `bonus`
        balance_after=balance.total_point_balance
    )
    db.add(transaction)

    # ✅ DB保存
    db.commit()

    return {"success": True, "message": f"✅ `{rule_name}` が適用されました！", "point_change": rule.point_value}
