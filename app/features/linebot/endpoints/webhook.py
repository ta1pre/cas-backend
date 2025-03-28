import asyncio
import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.features.linebot.services.user_info import fetch_user_info_by_line_id
from app.features.linebot.services.faq_search import search_faq
from app.features.linebot.services.line_client import send_line_reply
from app.scripts.fetch_microcms_faq import fetch_and_embed_faq
from fastapi import APIRouter, Query, HTTPException  # Queryを追加
from fastapi.responses import StreamingResponse  # StreamingResponseを追加
from app.features.linebot.services.user_info import fetch_user_info_by_line_id  # user_infoを取得する関数をインポート


# ロガー設定
logger = logging.getLogger("webhook")

router = APIRouter()

# データベースセッションを取得する関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/w")
async def messaging_webhook(request: Request, db: Session = Depends(get_db)):
    """
    LINE Webhookエンドポイント
    """
    try:
        # ヘッダーを取得
        headers = dict(request.headers)
        logger.debug(f"Webhook headers: {headers}")
        
        # リクエストボディを取得
        body = await request.body()
        logger.debug(f"Webhook raw body: {body}")
        
        body_json = await request.json()
        logger.debug(f"Webhook body JSON: {body_json}")
        
        events = body_json.get("events", [])

        # イベントが存在しない場合
        if not events:
            logger.info("イベントが存在しないので検証成功とみなします（正常なWebhookリクエストではありません）")
            return {"message": "Webhook verification successful"}

        for event in events:
            logger.debug(f"イベント処理: {event}")
            if event.get("type") == "message" and event["message"]["type"] == "text":
                line_id = event["source"]["userId"]
                reply_token = event["replyToken"]
                user_message = event["message"]["text"]
                
                logger.debug(f"ユーザーからのメッセージ: {user_message}, reply_token: {reply_token}")

                # ユーザー情報を取得
                user_info = fetch_user_info_by_line_id(db, line_id)
                logger.debug(f"ユーザー情報: {user_info}")

                # search_faq()内でsend_line_reply()を実行し、ここではreplyを返さない
                try:
                    result = search_faq(user_message, user_info, reply_token)
                    logger.debug(f"search_faqの結果: {result}")
                except Exception as e:
                    logger.error(f"search_faqのエラー: {str(e)}")
                    raise

        return {"message": "Webhook received successfully"}

    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Webhookエラー: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    
@router.api_route("/update-faq/", methods=["GET", "POST"])
async def update_faq(pw: str = Query(None, alias="pw")):  # "pw"を追加
    """
    MicroCMSからFAQを取得し、更新するAPI
    """

    # 認証パスワード
    AUTH_PASSWORD = "amayakachite"  # 認証パスワードを設定
    if pw != AUTH_PASSWORD:  # "password"を"pw"に変更
        raise HTTPException(status_code=401, detail="Unauthorized: パスワードが違います")

    # ストリーミングレスポンスで更新中...を表示
    async def event_generator():
        yield "data: FAQ更新中...\n\n"  # 表示文字を変更
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, fetch_and_embed_faq)
        yield "data: FAQ更新完了！！\n\n"  # 表示文字を変更

    return StreamingResponse(event_generator(), media_type="text/event-stream")