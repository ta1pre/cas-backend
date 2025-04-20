from sqlalchemy.orm import Session
from app.db.models.resv_reservation import ResvReservation
from app.features.points.services.apply_point_rule_service import apply_point_rule

def grant_cast_reward_points(db: Session, reservation_id: int):
    """
    予約が完了した際にキャストへ報酬ポイントを付与する（ルールベース）
    二重付与防止のため、cast_rewardedフラグで管理
    """
    reservation = db.query(ResvReservation).filter(ResvReservation.id == reservation_id).first()
    if not reservation or reservation.status != "completed":
        return  # 完了以外は何もしない

    # 二重付与防止
    if getattr(reservation, "cast_rewarded", False):
        return

    points = reservation.cast_reward_points or 0
    cast_id = reservation.cast_id
    if not cast_id or points <= 0:
        return

    # ルールベースでポイント付与
    apply_point_rule(
        db,
        user_id=cast_id,
        rule_name="cast_reward",
        variables={"amount": points, "reservation_id": reservation_id},
        transaction_type="reservation_payment"
    )

    # フラグを立ててコミット
    reservation.cast_rewarded = True
    db.commit()
