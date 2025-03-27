from sqlalchemy.orm import Session
from .status_history_repository import insert_status_history
from .reservation_repository import update_reservation_status, get_current_status

def change_status(db: Session, reservation_id: int, user_id: int, new_status: str, latitude: float = None, longitude: float = None):
    """
    ステータスを変更し、履歴を記録
    """
    try:
        prev_status = get_current_status(db, reservation_id)  # ✅ 変更前のステータスを取得

        insert_status_history(db, reservation_id, user_id, prev_status, new_status, latitude, longitude)  # ✅ 履歴を記録
        update_reservation_status(db, reservation_id, new_status, latitude, longitude)  # ✅ 予約のステータスを更新

        return {"message": f"予約 {reservation_id} のステータスを {new_status} に変更しました"}

    except Exception as e:
        db.rollback()
        return {"error": str(e)}
