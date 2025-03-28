import asyncio
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.features.linebot.services.user_info import fetch_user_info_by_line_id
from app.features.linebot.services.faq_search import search_faq
from app.features.linebot.services.line_client import send_line_reply
from app.scripts.fetch_microcms_faq import fetch_and_embed_faq
from fastapi import APIRouter, Query, HTTPException  # Query を追加
from fastapi.responses import StreamingResponse  # StreamingResponse を追加
from app.features.linebot.services.user_info import fetch_user_info_by_line_id  # `user_info` を取得する関数をインポート
import os
import logging
import json

# ロガーの設定
logger = logging.getLogger("webhook")
logger.setLevel(logging.DEBUG)


router = APIRouter()

# データベース依存関係を取得
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/w")
async def messaging_webhook(request: Request, db: Session = Depends(get_db)):
    """
    LINE Webhook のエンドポイント
    """
    try:
        # リクエストヘッダーをログに記録
        logger.debug(f"Webhook headers: {dict(request.headers)}")
        
        # リクエストボディを取得
        body = await request.body()
        logger.debug(f"Webhook raw body: {body}")
        
        # 環境変数のデバッグ出力
        line_channel_secret = os.environ.get("LINE_CHANNEL_SECRET")
        line_channel_access_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
        logger.debug(f"LINE_CHANNEL_SECRET exists: {line_channel_secret is not None}")
        logger.debug(f"LINE_CHANNEL_ACCESS_TOKEN exists: {line_channel_access_token is not None}")
        
        try:
            body_json = await request.json()
            logger.debug(f"Webhook body JSON: {json.dumps(body_json)}")
            events = body_json.get("events", [])
        except Exception as json_error:
            logger.error(f"JSON解析エラー: {json_error}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(json_error)}")

        if not events:
            logger.warning("No events found in the request")
            raise HTTPException(status_code=400, detail="No events found in the request")

        for event in events:
            logger.debug(f"Processing event: {json.dumps(event)}")
            if event.get("type") == "message" and event["message"]["type"] == "text":
                line_id = event["source"]["userId"]
                reply_token = event["replyToken"]
                user_message = event["message"]["text"]
                
                logger.debug(f"User message: {user_message}")
                logger.debug(f"LINE ID: {line_id}")
                logger.debug(f"Reply token: {reply_token}")

                # `user_info` を取得
                user_info = fetch_user_info_by_line_id(db, line_id)
                logger.debug(f"User info: {user_info}")

                # `search_faq()` 内で `send_line_reply()` を呼ぶため、ここでは `reply` を返すだけ
                search_faq(user_message, user_info, reply_token)

        return {"message": "Webhook received successfully"}

    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f" Webhookエラー: {e}")
        logger.exception("詳細なエラー情報:")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    
@router.api_route("/update-faq/", methods=["GET", "POST"])
async def update_faq(pw: str = Query(None, alias="pw")):  
    """
    MicroCMSからFAQデータを取得し、埋め込みを生成して保存するAPI
    """

    # 簡単なパスワード認証
    AUTH_PASSWORD = "amayakachite"  
    if pw != AUTH_PASSWORD:  
        raise HTTPException(status_code=401, detail="Unauthorized: パスワードが違います")

    # ストリーミングレスポンスで「更新中...」を表示
    async def event_generator():
        yield "data: FAQ更新を開始しました...\n\n"  
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, fetch_and_embed_faq)
        yield "data: FAQ更新が完了しました！\n\n"  

    return StreamingResponse(event_generator(), media_type="text/event-stream")