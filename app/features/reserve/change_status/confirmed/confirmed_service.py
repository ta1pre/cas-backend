import logging
from sqlalchemy.orm import Session
from app.features.reserve.change_status.confirmed.confirmed_repository import get_user_points, get_reservation_total
from app.features.points.services.apply_point_rule_service import apply_point_rule

def run_action(db: Session, reservation_id: int, user_id: int):
    """
    `confirmed` ステータスの事前処理:
    1. ユーザーのポイント残高を確認
    2. ポイントが不足している場合は `status="INSUFFICIENT_POINTS"` を返す
    3. 足りている場合は `"OK"` を返す（DBの変更はしない）
    """
    # <<< デバッグログ追加 >>>
    print(f"\n🔥🔥🔥 confirmed_service.run_action が呼び出されました！ reservation_id={reservation_id}, user_id={user_id} 🔥🔥🔥\n")
    # <<< デバッグログ追加完了 >>>
    
    logging.info(f"🔄 `confirmed` ステータス処理を実行中: reservation_id={reservation_id} user_id={user_id}")

    # ✅ ユーザーの現在のポイント残高を取得
    user_points = get_user_points(db, user_id)
    if user_points is None:
        logging.error(f"🚨 ユーザー {user_id} のポイント情報が取得できません")
        return {"status": "ERROR", "message": "ポイント情報を取得できません"}

    logging.info(f"✅ ユーザー {user_id} のポイント確認OK: {user_points} ポイント所持")

    # ✅ 予約の合計ポイントを取得
    total_points = get_reservation_total(db, reservation_id)
    if total_points is None:
        logging.error(f"🚨 予約 {reservation_id} の合計ポイント情報が取得できません")
        return {"status": "ERROR", "message": "予約情報を取得できません"}

    logging.info(f"📌 予約 {reservation_id} に必要なポイント: {total_points}")

    # ✅ ポイントが不足している場合
    if user_points < total_points:
        shortfall = total_points - user_points
        logging.warning(f"⚠️ ポイント不足: 必要 {total_points}, 所持 {user_points}, 不足 {shortfall}")
        return {
            "status": "INSUFFICIENT_POINTS",
            "shortfall": shortfall,
            "message": f"ポイントが不足しています（不足: {shortfall}）"
        }

    # ✅ ポイントが足りている場合 → ポイント使用処理を実行
    payment_result = apply_point_rule(
        db, 
        user_id, 
        "reservation_payment", 
        {
            "amount": -total_points,  # マイナス値にする
            "reservation_id": reservation_id,
            "description": f"予約ID:{reservation_id}のポイント使用"
        }
    )
    
    if not payment_result.get("success", False):
        logging.error(f"🚨 ポイント使用処理に失敗しました: {payment_result.get('message', '不明なエラー')}")
        return {"status": "ERROR", "message": payment_result.get("message", "ポイント使用処理に失敗しました")}

    # ✅ ポイント使用処理成功 → "OK" を返す（ステータス変更は `common.py` で実行）
    logging.info(f"✅ `confirmed` の事前処理完了: 予約ID {reservation_id}")

    consumed_points = abs(payment_result.get("point_change", 0))
    return {
        "status": "OK", 
        "message": f"予約ポイント使用処理完了、{consumed_points} ポイントを使用しました",
        "payment_info": {
            "amount": total_points,
            "new_balance": payment_result.get("new_balance", 0),
            "transaction_id": payment_result.get("transaction_id"),
            "consumed_points": consumed_points
        }
    }
