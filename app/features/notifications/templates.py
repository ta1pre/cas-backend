# app/features/notifications/templates.py

TEMPLATES = {
    "reservation_created": "✅ 予約リクエストを送信しました。\n\n📍 場所: {location}\n📅 日時: {date} {time}",
    "reservation_canceled": "❌ 予約がキャンセルされました。\n\n📍 場所: {location}\n📅 日時: {date} {time}",
    "reservation_confirmed": "予約が確定しました！\n予約番号：{reservation_id}\nキャスト：{cast_name}\n開始日時：{date} {time}\n\n待ち合わせ場所に到着後、予約詳細ページの「到着」ボタンを押して下さい。\n\n🔗 予約詳細：\nhttps://cas.tokyo/p/customer/reserve/#{reservation_id}",
}

def get_template(notification_type: str) -> str:
    """
    指定された通知タイプのテンプレートを取得
    """
    return TEMPLATES.get(notification_type, "⚠️ 通知テンプレートが見つかりません")
