# app/features/notifications/templates.py

TEMPLATES = {
    "reservation_created": "✅ 予約リクエストを送信しました。\n\n📍 場所: {location}\n📅 日時: {date} {time}",
    "reservation_canceled": "❌ 予約がキャンセルされました。\n\n📍 場所: {location}\n📅 日時: {date} {time}",
}

def get_template(notification_type: str) -> str:
    """
    指定された通知タイプのテンプレートを取得
    """
    return TEMPLATES.get(notification_type, "⚠️ 通知テンプレートが見つかりません")
