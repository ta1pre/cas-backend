import asyncio
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.features.linebot.services.user_info import fetch_user_info_by_line_id
from app.features.linebot.services.faq_search import search_faq
from app.features.linebot.services.line_client import send_line_reply
from app.scripts.fetch_microcms_faq import fetch_and_embed_faq
from fastapi import APIRouter, Query, HTTPException  # ✅ Query を追加
from fastapi.responses import StreamingResponse  # ✅ StreamingResponse を追加
from app.features.linebot.services.user_info import fetch_user_info_by_line_id  # ✅ `user_info` を取得する関数をインポート


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
        body_json = await request.json()
        events = body_json.get("events", [])

        if not events:
            raise HTTPException(status_code=400, detail="No events found in the request")

        for event in events:
            if event.get("type") == "message" and event["message"]["type"] == "text":
                line_id = event["source"]["userId"]
                reply_token = event["replyToken"]
                user_message = event["message"]["text"]

                # ✅ `user_info` を取得
                user_info = fetch_user_info_by_line_id(db, line_id)

                # ✅ `search_faq()` 内で `send_line_reply()` を呼ぶため、ここでは `reply` を返すだけ
                search_faq(user_message, user_info, reply_token)

        return {"message": "Webhook received successfully"}

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Webhookエラー: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    
@router.api_route("/update-faq/", methods=["GET", "POST"])
async def update_faq(pw: str = Query(None, alias="pw")):  # ✅ "pw" に変更
    """
    MicroCMSからFAQデータを取得し、埋め込みを生成して保存するAPI
    """

    # ① 簡単なパスワード認証
    AUTH_PASSWORD = "amayakachite"  # ✅ 任意のパスワードを設定
    if pw != AUTH_PASSWORD:  # ✅ "password" → "pw" に変更
        raise HTTPException(status_code=401, detail="Unauthorized: パスワードが違います")

    # ② ストリーミングレスポンスで「更新中...」を表示
    async def event_generator():
        yield "data: FAQ更新を開始しました...\n\n"  # すぐに表示される
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, fetch_and_embed_faq)
        yield "data: FAQ更新が完了しました！\n\n"  # 更新終了メッセージ

    return StreamingResponse(event_generator(), media_type="text/event-stream")