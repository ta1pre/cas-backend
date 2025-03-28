# app/features/reserve/endpoints/common.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.features.reserve.repositories.common.get_message_repository import fetch_db_messages
import logging

common_router = APIRouter()

@common_router.post("/test")
def test_common():
    return {"message": "Common endpoint is working"}

@common_router.post("/messages_get")
def fetch_messages(request: dict, db: Session = Depends(get_db)):
    user_id = request.get("user_id")
    reservation_id = request.get("reservation_id")

    if not user_id or not reservation_id:
        raise HTTPException(status_code=400, detail="user_id と reservation_id は必須です")  # ✅ ここで400エラー

    return fetch_db_messages(db, user_id, reservation_id)
  

# ✅ メッセージ送信API
from app.features.reserve.repositories.common.send_message_repository import save_message
from app.features.reserve.schemas.common.send_message_schema import MessageCreateRequest, MessageCreateResponse

@common_router.post("/messages_send", response_model=MessageCreateResponse)
def send_message(request: MessageCreateRequest, db: Session = Depends(get_db)):
    if not request.user_id or not request.reservation_id or not request.message:
        raise HTTPException(status_code=400, detail="user_id, reservation_id, message は必須です")

    return save_message(db, request)


#✅ ステータスが変わる時のAPI
# requested 初回なので処理はここではしなくてOK
# adjusting ユーザーから修正依頼があったとき(ユーザーが送る)
# waiting_user_confirm キャストから修正案を提案する時(キャストが送る)
# confirmed ユーザーが予約確定を押した時(ユーザーが送る)
# サービス終了までのエンドポイントここで作っていく(user_arrivedとか)

from app.features.reserve.change_status.hooks.change_status.change_status_schema import ChangeStatusRequest
from app.features.reserve.change_status.hooks.change_status.change_status import change_status

import importlib
import traceback

@common_router.post("/change_status/{next_status}")
def change_status_endpoint(
    next_status: str,
    request: ChangeStatusRequest,
    db: Session = Depends(get_db)
):
    """
    `{next_status}` に基づいて、対応するディレクトリから `{next_status}_service.py` を動的に読み込む。
    
    ✅ ルール：
    1. `run_action()` が存在すれば実行（ない場合はスキップ）
    2. `run_action()` は `status` を返す（例: "OK", "INSUFFICIENT_POINTS", "GPS_REQUIRED"）
    3. `common.py` では `run_action()` の `status` をそのままフロントへ返す
    4. `run_action()` は DB の更新をせず、変更は `change_status()` に委ねる

    このルールにより、新しいステータスを追加する際に `{next_status}_service.py` を作るだけで対応可能。
    """
    try:
        logging.info(f"🟡 next_status={next_status}, 受信データ: {request.dict()}")

        # 動的に `{next_status}/{next_status}_service.py` を読み込む
        service_module_name = f"app.features.reserve.change_status.{next_status}.{next_status}_service"

        try:
            service_module = importlib.import_module(service_module_name)
            if hasattr(service_module, "run_action"):
                action_result = service_module.run_action(db, request.reservation_id, request.user_id)
                logging.info(f"{service_module_name}.run_action() を実行しました。")

                # ✅ `status` が "OK" の場合 → ステータス更新を実行
                if action_result.get("status") == "OK":
                    return change_status(
                        db=db,
                        reservation_id=request.reservation_id,
                        user_id=request.user_id,
                        new_status=next_status,
                        latitude=request.latitude,
                        longitude=request.longitude
                    )
                
                # ✅ それ以外（例: ポイント不足, GPSエラーなど）はそのまま返す
                return action_result  

            else:
                logging.info(f"{service_module_name} に run_action() が定義されていません。スルー。")

        except ModuleNotFoundError:
            logging.info(f"{service_module_name} が見つかりません。個別処理なしで進行。")

        # ✅ `run_action()` がない場合でも `change_status()` を実行
        return change_status(
            db=db,
            reservation_id=request.reservation_id,
            user_id=request.user_id,
            new_status=next_status,
            latitude=request.latitude,
            longitude=request.longitude
        )

    except Exception as e:
        logging.error(f"🚨 エラー発生: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
