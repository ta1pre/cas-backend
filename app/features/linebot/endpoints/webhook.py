import asyncio
from fastapi import APIRouter, Request, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.features.linebot.services.user_info import fetch_user_info_by_line_id
from app.features.linebot.services.faq_search import search_faq
from app.features.linebot.services.line_client import send_line_reply
from app.scripts.fetch_microcms_faq import fetch_and_embed_faq
from fastapi import APIRouter, Query, HTTPException  # Query を追加
from fastapi.responses import StreamingResponse  # StreamingResponse を追加
from app.features.linebot.services.user_info import fetch_user_info_by_line_id  # `user_info` を取得する関数をインポート
import hmac
import hashlib
import base64
import os
import logging

# ロガーの設定
logger = logging.getLogger(__name__)

router = APIRouter()

# LINE Channel Secret (環境変数から取得)
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', '')

# データベース依存関係を取得
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/w")
async def messaging_webhook(request: Request, db: Session = Depends(get_db), x_line_signature: str = Header(None)):
    """
    LINE Webhook のエンドポイント
    """
    try:
        # リクエストボディを取得
        body = await request.body()
        body_text = body.decode('utf-8')
        
        # デバッグ情報をログに出力
        logger.info(f"Received webhook request with signature: {x_line_signature}")
        logger.info(f"Request body: {body_text}")
        
        # 署名検証
        if LINE_CHANNEL_SECRET and x_line_signature:
            hash = hmac.new(LINE_CHANNEL_SECRET.encode('utf-8'), body, hashlib.sha256).digest()
            signature = base64.b64encode(hash).decode('utf-8')
            
            # 署名が一致しない場合はエラー
            if signature != x_line_signature:
                logger.error(f"Invalid signature. Expected: {signature}, Got: {x_line_signature}")
                raise HTTPException(status_code=403, detail="Invalid signature")
        else:
            logger.warning("Signature verification skipped: LINE_CHANNEL_SECRET or X-Line-Signature not provided")
        
        # JSONパース
        try:
            body_json = await request.json()
            logger.info(f"Parsed JSON: {body_json}")
        except Exception as json_error:
            logger.error(f"JSON parse error: {json_error}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(json_error)}")
            
        events = body_json.get("events", [])
        
        if not events:
            logger.warning("No events found in the request")
            raise HTTPException(status_code=400, detail="No events found in the request")

        for event in events:
            logger.info(f"Processing event: {event}")
            if event.get("type") == "message" and event["message"]["type"] == "text":
                line_id = event["source"]["userId"]
                reply_token = event["replyToken"]
                user_message = event["message"]["text"]
                
                logger.info(f"Message from user {line_id}: {user_message}")

                # `user_info` を取得
                user_info = fetch_user_info_by_line_id(db, line_id)

                # `search_faq()` 内で `send_line_reply()` を呼ぶため、ここでは `reply` を返すだけ
                search_faq(user_message, user_info, reply_token)

        return {"message": "Webhook received successfully"}

    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f" Webhookエラー: {e}", exc_info=True)
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