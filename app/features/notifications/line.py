# app/features/notifications/line.py

import requests
from app.core.config import LINE_CHANNEL_ACCESS_TOKEN

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"

def send_line_message(user_line_id: str, message: str):
    """
    指定したLINEユーザーにメッセージを送信
    """
    if not user_line_id:
        print("❌ 無効なLINEユーザーID")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }

    payload = {
        "to": user_line_id,
        "messages": [{"type": "text", "text": message}]
    }

    response = requests.post(LINE_PUSH_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"❌ LINEメッセージ送信失敗: {response.status_code}, {response.text}")
    else:
        print(f"✅ LINEメッセージ送信成功: {user_line_id}")
