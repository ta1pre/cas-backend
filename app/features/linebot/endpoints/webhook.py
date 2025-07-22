import asyncio
import logging
import hmac
import hashlib
import base64
import json
import os
from fastapi import APIRouter, Request, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.features.linebot.services.user_info import fetch_user_info_by_line_id
from app.features.linebot.services.faq_search import search_faq
from app.features.linebot.services.line_client import send_line_reply
from app.scripts.fetch_microcms_faq import fetch_and_embed_faq
from app.features.linebot.rich_menu.services.menu_manager import MenuManager
from fastapi import APIRouter, Query, HTTPException  
from fastapi.responses import StreamingResponse  
from app.features.linebot.services.user_info import fetch_user_info_by_line_id  
from app.core.config import LINE_CHANNEL_SECRET


# ロガー設定
logger = logging.getLogger("webhook")

# AWS環境かどうかを判定
is_aws = os.getenv("AWS_EXECUTION_ENV") is not None or os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None

router = APIRouter()

# データベースセッションを取得する関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/w")
async def messaging_webhook(request: Request, db: Session = Depends(get_db), x_line_signature: str = Header(None)):
    """
    LINE Webhookエンドポイント
    """
    try:
        # リクエスト情報をログに記録
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"Webhookリクエスト受信: クライアントIP={client_host}")
        
        # ヘッダーを取得
        headers = dict(request.headers)
        logger.debug(f"Webhookヘッダー: {headers}")
        
        # 署名検証用のヘッダーを確認
        if not x_line_signature:
            logger.error("X-Line-Signatureヘッダーがありません")
            return {"message": "X-Line-Signature is missing"}
        
        # リクエストボディを取得
        body = await request.body()
        body_text = body.decode('utf-8', errors='replace')
        
        # ボディが空でないか確認
        if not body_text or body_text.isspace():
            logger.error("リクエストボディが空です")
            return {"message": "Empty request body"}
            
        logger.debug(f"Webhookリクエストボディ: {body_text[:200]}..." if len(body_text) > 200 else f"Webhookリクエストボディ: {body_text}")
        
        # 署名を検証
        if LINE_CHANNEL_SECRET:
            try:
                hash = hmac.new(LINE_CHANNEL_SECRET.encode('utf-8'), body, hashlib.sha256).digest()
                signature = base64.b64encode(hash).decode('utf-8')
                
                logger.debug(f"計算された署名: {signature}")
                logger.debug(f"受信した署名: {x_line_signature}")
                
                if signature != x_line_signature:
                    logger.error("署名検証に失敗しました")
                    if is_aws:
                        # AWS環境では詳細情報をログに出力
                        logger.error(f"署名検証失敗の詳細 - 計算値: {signature}, 受信値: {x_line_signature}, ボディ長: {len(body)}")
                    return {"message": "Invalid signature"}
                
                logger.info("署名検証に成功しました")
            except Exception as e:
                logger.error(f"署名検証中にエラーが発生しました: {str(e)}")
                return {"message": "Signature verification error"}
        else:
            logger.warning("LINE_CHANNEL_SECRETが設定されていないため、署名検証をスキップします")
        
        # JSONパース
        try:
            body_json = json.loads(body_text)
            logger.debug(f"WebhookボディJSON: {json.dumps(body_json, ensure_ascii=False)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSONパースエラー: {str(e)}, ボディ: {body_text[:100]}")
            return {"message": "Invalid JSON format"}
        except Exception as e:
            logger.error(f"JSONパース中の予期せぬエラー: {str(e)}")
            return {"message": "Error processing request body"}
        
        events = body_json.get("events", [])

        # イベントが存在しない場合
        if not events:
            logger.info("イベントが存在しないので検証成功とみなします（正常なWebhookリクエストではありません）")
            return {"message": "Webhook verification successful"}

        logger.info(f"処理するイベント数: {len(events)}")
        
        for event in events:
            logger.debug(f"イベント処理: {json.dumps(event, ensure_ascii=False)}")
            
            # イベントタイプの確認
            event_type = event.get("type")
            
            # followイベントの処理
            if event_type == "follow":
                await handle_follow_event(event, db)
                continue
                
            # messageイベント以外はスキップ
            if event_type != "message":
                logger.info(f"未対応のイベント: {event_type}")
                continue
                
            # メッセージタイプの確認
            message = event.get("message", {})
            message_type = message.get("type")
            if message_type != "text":
                logger.info(f"テキスト以外のメッセージ: {message_type}")
                continue
            
            # 必要な情報を取得
            line_id = event.get("source", {}).get("userId")
            reply_token = event.get("replyToken")
            user_message = message.get("text", "")
            
            if not line_id or not reply_token or not user_message:
                logger.error(f"必要な情報が不足しています: line_id={line_id}, reply_token={reply_token}, message={user_message}")
                continue
            
            logger.info(f"ユーザーからのメッセージ: {user_message}, reply_token={reply_token}, line_id={line_id}")

            # ユーザー情報を取得
            try:
                user_info = fetch_user_info_by_line_id(db, line_id)
                logger.debug(f"ユーザー情報: {user_info}")
                
                # Rich Menu更新処理を追加
                try:
                    menu_manager = MenuManager()
                    menu_result = menu_manager.update_user_menu(line_id, user_info)
                    logger.debug(f"Rich Menu更新結果: {menu_result}")
                except Exception as menu_error:
                    logger.error(f"Rich Menu更新エラー: {str(menu_error)}")
                    
            except Exception as e:
                logger.error(f"ユーザー情報取得エラー: {str(e)}")
                user_info = {"id": None}

            # search_faq()内でsend_line_reply()を実行
            try:
                logger.info(f"FAQを検索します: クエリ='{user_message}'")
                result = search_faq(user_message, user_info, reply_token)
                logger.debug(f"search_faqの結果: {result}")
            except Exception as e:
                logger.error(f"search_faqのエラー: {str(e)}")
                try:
                    # エラー時にもユーザーに返信
                    logger.info("エラーメッセージをユーザーに送信します")
                    send_line_reply(reply_token, "申し訳ありません。現在システムに問題が発生しています。しばらくしてから再度お試しください。")
                except Exception as reply_error:
                    logger.error(f"エラー返信中にさらにエラー: {str(reply_error)}")

        logger.info("Webhookの処理が正常に完了しました")
        return {"message": "Webhook received successfully"}

    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Webhookエラー: {str(e)}")
        # エラーの詳細をログに出力
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.api_route("/update-faq/", methods=["GET", "POST"])
async def update_faq(pw: str = Query(None, alias="pw"), use_stream: bool = Query(False, alias="stream")):
    """
    MicroCMSからFAQを取得し、更新するAPI
    パラメーター:
        pw: 認証パスワード
        use_stream: Trueの場合、ストリーミングレスポンスで更新中...を表示、Falseの場合、JSONレスポンスで更新結果を返す
    """
    logger.info("FAQ更新処理開始")

    # 認証パスワード
    AUTH_PASSWORD = "amayakachite"
    if pw != AUTH_PASSWORD:
        logger.warning("認証パスワード不一致: パスワードが違います")
        raise HTTPException(status_code=401, detail="Unauthorized: パスワードが違います")

    # ストリーミングレスポンスで更新中...を表示
    if use_stream:
        logger.info("ストリーミングレスポンスでFAQ更新中...を表示します")
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    
    # JSONレスポンスで更新結果を返す
    try:
        logger.info("JSONレスポンスでFAQ更新結果を返します")
        result = fetch_and_embed_faq()
        if result:
            logger.info("FAQ更新処理成功")
            return {"status": "success", "message": "FAQ更新完了！！"}
        else:
            logger.error("FAQ更新処理失敗")
            return {"status": "error", "message": "FAQ更新失敗しました。"}
    except Exception as e:
        logger.error(f"FAQ更新処理中にエラーが発生しました: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"エラーが発生しました: {str(e)}")


# ストリーミングレスポンス用イベントジェネレーター
async def event_generator():
    logger.info("イベントジェネレーターを開始します")
    yield "data: FAQ更新中...\n\n"
    loop = asyncio.get_event_loop()
    try:
        logger.info("fetch_and_embed_faqを実行します")
        result = await loop.run_in_executor(None, fetch_and_embed_faq)
        if result:
            logger.info("FAQ更新処理成功")
            yield "data: FAQ更新完了！！\n\n"
        else:
            logger.error("FAQ更新処理失敗")
            yield "data: FAQ更新失敗しました。\n\n"
    except Exception as e:
        logger.error(f"FAQ更新処理中にエラーが発生しました: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        yield f"data: エラーが発生しました: {str(e)}\n\n"
    finally:
        logger.info("イベントジェネレーターを終了します")
        yield "data: 処理完了\n\n"


async def handle_follow_event(event: dict, db: Session):
    """
    followイベント（友だち追加）の処理
    """
    try:
        # LINE IDを取得
        line_id = event.get("source", {}).get("userId")
        
        if not line_id:
            logger.error("followイベントでLINE IDが取得できません")
            return
        
        logger.info(f"新しいフォロワー: {line_id}")
        
        # ユーザー情報を取得
        try:
            user_info = fetch_user_info_by_line_id(db, line_id)
            logger.info(f"フォロワーのユーザー情報: {user_info}")
        except Exception as e:
            logger.error(f"ユーザー情報取得エラー: {str(e)}")
            user_info = {"id": None, "type": None}
        
        # Rich Menuを適用
        try:
            menu_manager = MenuManager()
            result = menu_manager.update_user_menu(line_id, user_info)
            logger.info(f"Rich Menu適用結果: {result}")
            
            if result.get("success"):
                logger.info(f"Rich Menu適用成功: {result.get('menu_type')}")
            else:
                logger.error(f"Rich Menu適用失敗: {result.get('message')}")
                
        except Exception as e:
            logger.error(f"Rich Menu適用エラー: {str(e)}")
        
        # ウェルカムメッセージを送信（reply_tokenがある場合のみ）
        reply_token = event.get("replyToken")
        if reply_token:
            try:
                welcome_message = get_welcome_message(user_info)
                send_line_reply(reply_token, welcome_message)
                logger.info("ウェルカムメッセージ送信完了")
            except Exception as e:
                logger.error(f"ウェルカムメッセージ送信エラー: {str(e)}")
        
    except Exception as e:
        logger.error(f"followイベント処理エラー: {str(e)}")


def get_welcome_message(user_info: dict) -> str:
    """ユーザータイプに応じたウェルカムメッセージを生成"""
    user_type = user_info.get("type")
    nickname = user_info.get("nickname", "")
    
    if user_type == "cast":
        return f"キャスト{nickname}さん、PreCas公式LINEへようこそ！\nメニューから予約管理や売上確認ができます。"
    elif user_type == "customer":
        return f"{nickname}さん、PreCas公式LINEへようこそ！\nメニューからキャスト検索や予約ができます。"
    else:
        return "PreCas公式LINEへようこそ！\nまずはメニューから会員登録をお願いします。"