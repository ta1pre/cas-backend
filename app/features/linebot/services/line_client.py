import requests
from fastapi import HTTPException
from app.core.config import LINE_CHANNEL_ACCESS_TOKEN

LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"

def send_line_reply(reply_token: str, message: str, quick_reply: bool = False):
    """
    LINEユーザーへ返信（Quick Reply もまとめて送るオプションあり）
    """
    if not reply_token:
        print("❌ 無効な reply_token が渡されました")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
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

    response = requests.post(LINE_REPLY_URL, headers=headers, json=data)
    if response.status_code != 200:
        print(f"❌ LINEメッセージ送信失敗: {response.status_code}, {response.text}")

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
