from sqlalchemy.orm import Session
from .status_history_repository import insert_status_history
from .reservation_repository import update_reservation_status, get_current_status
from app.features.notifications.dispatcher import send 

def change_status(db: Session, reservation_id: int, user_id: int, new_status: str, latitude: float = None, longitude: float = None):
    """
    ステータスを変更し、履歴を記録
    """
    try:
        prev_status = get_current_status(db, reservation_id)  

        insert_status_history(db, reservation_id, user_id, prev_status, new_status, latitude, longitude)  
        update_reservation_status(db, reservation_id, new_status, latitude, longitude)  

        # === ポイント付与処理（完了時のみ） ===
        if new_status == 'completed':
            from app.features.points.services.cast_reward_service import grant_cast_reward_points
            grant_cast_reward_points(db, reservation_id)
        # === ポイント付与処理ここまで ===

        # === 通知処理を追加 ===
        if new_status == 'confirmed':
            try:
                print(f"\n 予約確定通知を送信します: reservation_id={reservation_id}, user_id={user_id}\n")
                send(
                    notification_type="reservation_confirmed",
                    db=db,
                    reservation_id=reservation_id,
                    user_id=user_id
                )
                print(f"\n 予約確定通知のディスパッチ完了: reservation_id={reservation_id}\n")
            except Exception as notify_e:
                # 通知処理でのエラーは本体処理に影響させない
                print(f"\n 予約確定通知の送信中にエラーが発生: {notify_e}\n")
        # === 通知処理を追加完了 ===

        return {"message": f"予約 {reservation_id} のステータスを {new_status} に変更しました"}

    except Exception as e:
        db.rollback()
        return {"error": str(e)}
