import logging
from sqlalchemy.orm import Session
from app.features.reserve.change_status.confirmed.confirmed_repository import get_user_points, get_reservation_total

def run_action(db: Session, reservation_id: int, user_id: int):
    """
    `confirmed` ステータスの事前処理:
    1. ユーザーのポイント残高を確認
    2. ポイントが不足している場合は `status="INSUFFICIENT_POINTS"` を返す
    3. 足りている場合は `"OK"` を返す（DBの変更はしない）
    """
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

    # ✅ ポイントが足りている場合 → "OK" を返す（ステータス変更は `common.py` で実行）
    logging.info(f"✅ `confirmed` の事前処理完了: 予約ID {reservation_id}")

    return {"status": "OK", "message": "ポイント確認完了"}
