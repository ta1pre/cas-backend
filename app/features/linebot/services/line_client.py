import requests
from fastapi import HTTPException
from app.core.config import LINE_CHANNEL_ACCESS_TOKEN
import logging
import json
import traceback
import os
import time

# ロガーの設定
logger = logging.getLogger("line_client")

# AWS環境かどうかを判定
is_aws = os.getenv("AWS_EXECUTION_ENV") is not None or os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None

LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"

def send_line_reply(reply_token: str, message: str, quick_reply: bool = False):
    """
    LINEユーザーへ返信（Quick Reply もまとめて送るオプションあり）
    """
    start_time = time.time()
    logger.info(f"LINE APIリクエスト送信: reply_token={reply_token[:5]}...{reply_token[-5:]}")
    
    if not reply_token:
        logger.error("❌ 無効な reply_token が渡されました")
        return False

    if not LINE_CHANNEL_ACCESS_TOKEN:
        logger.error("❌ LINE_CHANNEL_ACCESS_TOKEN が設定されていません")
        return False

    logger.debug(f"reply_token: {reply_token}")
    
    # トークン長さを取得（長さが20文字以上の場合、ログ出力時に末尾10文字を省略）
    token_length = len(LINE_CHANNEL_ACCESS_TOKEN)
    logger.debug(f"LINE_CHANNEL_ACCESS_TOKEN: {LINE_CHANNEL_ACCESS_TOKEN[:5]}...{LINE_CHANNEL_ACCESS_TOKEN[-5:]} (長さ: {token_length}文字)")
    
    # Bearerトークン処理
    auth_token = LINE_CHANNEL_ACCESS_TOKEN
    if not auth_token.startswith("Bearer ") and not auth_token.startswith("bearer "):
        logger.info("LINE_CHANNEL_ACCESS_TOKENに 'Bearer ' を付与")
        auth_token = f"Bearer {auth_token}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_token
    }

    messages = [{"type": "text", "text": message}]

    # ✅ Quick Reply を含める場合（reply_token を1回で使い切る）
    if quick_reply:
        messages.append({
            "type": "text",
            "text": "この回答は役に立ちましたか？",
            "quickReply": {
                "items": [
                    {
                        "type": "action",
                        "action": {
                            "type": "message",
                            "label": "YES",
                            "text": "YES"
                        }
                    },
                    {
                        "type": "action",
                        "action": {
                            "type": "message",
                            "label": "NO",
                            "text": "NO"
                        }
                    }
                ]
            }
        })

    data = {
        "replyToken": reply_token,
        "messages": messages
    }

    # ログ出力（長さが500文字以上の場合、末尾200文字を省略）
    log_data = json.dumps(data, ensure_ascii=False)
    if len(log_data) > 500 and not is_aws:
        logger.debug(f"LINE APIリクエスト送信: {log_data[:200]}...(省略)...{log_data[-200:]}")
    else:
        logger.debug(f"LINE APIリクエスト送信: {log_data}")
    
    # ヘッダー情報のログ出力（Authorizationヘッダーの値を末尾10文字に省略）
    safe_headers = headers.copy()
    if "Authorization" in safe_headers:
        auth_value = safe_headers["Authorization"]
        if len(auth_value) > 20:
            safe_headers["Authorization"] = f"{auth_value[:10]}...{auth_value[-10:]}"
    logger.debug(f"LINE APIヘッダー: {safe_headers}")
    
    # リトライ回数とタイムアウト時間の設定
    max_retries = 3 if is_aws else 1  # AWS環境ではリトライ回数を増やす
    timeout_seconds = 10  # タイムアウト時間
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            # リクエスト送信
            logger.info(f"LINE APIリクエスト送信: 試行 {retry_count + 1}/{max_retries}")
            
            # タイムアウト時間を設定してリクエスト送信
            response = requests.post(LINE_REPLY_URL, headers=headers, json=data, timeout=timeout_seconds)
            
            # レスポンスログ
            logger.info(f"LINE APIレスポンス: ステータスコード={response.status_code}")
            logger.debug(f"LINE APIレスポンス: レスポンス={response.text}")
            
            if response.status_code != 200:
                error_msg = f"❌ LINEメッセージ送信失敗: ステータスコード={response.status_code}, レスポンス={response.text}"
                logger.error(error_msg)
                
                # エラーハンドリング
                if response.status_code == 400:
                    logger.error("❌ リクエストボディが不正です。データを確認してください。")
                    # 400エラーの場合、リトライしない
                    break
                elif response.status_code == 401:
                    logger.error("❌ 認証エラー: LINE_CHANNEL_ACCESS_TOKEN が無効です。")
                    # 401エラーの場合、リトライしない
                    break
                elif response.status_code == 403:
                    logger.error("❌ 権限エラー: このチャンネルではこの操作が許可されていません。")
                    # 403エラーの場合、リトライしない
                    break
                elif response.status_code == 429:
                    logger.error("❌ リクエスト制限超過: リクエスト送信速度が速すぎます。")
                    # 429エラーの場合、リトライする
                    if retry_count < max_retries - 1:
                        wait_time = 2 ** retry_count  # 指数関数で待機時間を増やす
                        logger.info(f"{wait_time}秒待機して再試行")
                        time.sleep(wait_time)
                        retry_count += 1
                        continue
                elif response.status_code == 500:
                    logger.error("❌ LINEサーバーエラー: 内部エラーが発生しました。")
                    # 500エラーの場合、リトライする
                    if retry_count < max_retries - 1:
                        wait_time = 1  # 1秒待機して再試行
                        logger.info(f"{wait_time}秒待機して再試行")
                        time.sleep(wait_time)
                        retry_count += 1
                        continue
                
                return False
            
            # 処理時間を計測
            elapsed_time = time.time() - start_time
            logger.info(f"✅ LINEメッセージ送信成功: 処理時間={elapsed_time:.2f}秒")
            return True
            
        except requests.exceptions.Timeout:
            logger.error(f"❌ LINE APIタイムアウト: 試行 {retry_count + 1}/{max_retries}")
            if retry_count < max_retries - 1:
                wait_time = 2 ** retry_count
                logger.info(f"{wait_time}秒待機して再試行")
                time.sleep(wait_time)
                retry_count += 1
                continue
            else:
                logger.error("❌ 最大リトライ回数に達しました。LINEメッセージ送信失敗")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ LINE APIリクエスト送信エラー: {str(e)}")
            if retry_count < max_retries - 1 and is_aws:
                wait_time = 2 ** retry_count
                logger.info(f"{wait_time}秒待機して再試行")
                time.sleep(wait_time)
                retry_count += 1
                continue
            else:
                return False
                
        except Exception as e:
            logger.error(f"❌ LINE API内部エラー: {str(e)}")
            logger.error(traceback.format_exc())  # スタックトレースをログに出す
            return False
        
        # リトライ回数を増やす
        retry_count += 1
    
    # リトライ回数に達した場合
    logger.error("❌ 最大リトライ回数に達しました。LINEメッセージ送信失敗")
    return False

def handle_yes_no_response(user_id: str, user_message: str, reply_token: str, user_conversations: dict):
    """
    YES/NO の応答を処理する
    """
    if user_message.upper() == "YES":
        # ✅ 履歴を削除
        if user_id in user_conversations:
            del user_conversations[user_id]
        send_line_reply(reply_token, "ありがとうございます！また質問があれば聞いてください😊")

    elif user_message.upper() == "NO":
        send_line_reply(reply_token, "分かりました！引き続き質問をどうぞ😊")
