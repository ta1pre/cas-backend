# app/features/notifications/templates.py

TEMPLATES = {
    "reservation_created": "#{reservation_id}\n{cast_name}さんに予約リクエストを送信しました。\nしばらくお待ち下さい。\n\n🔗 予約ページ\nhttps://cas.tokyo/p/customer/reserve#{reservation_id}",
    "reservation_created_cast": "#{reservation_id}\n新しい予約リクエストが届きました。\n\nお客様: {user_name}\n日時: {date} {time}\n場所: {location}\n\n🔗 予約ページ\nhttps://cas.tokyo/p/cast/reserve#{reservation_id}",
    "reservation_canceled": "❌ 予約がキャンセルされました。\n\n📍 場所: {location}\n📅 日時: {date} {time}",
    "reservation_confirmed": "予約が確定しました！\n予約番号：{reservation_id}\nキャスト：{cast_name}\n開始日時：{date} {time}\n\n待ち合わせ場所に到着後、予約詳細ページの「到着」ボタンを押して下さい。\n\n🔗 予約詳細：\nhttps://cas.tokyo/p/customer/reserve#{reservation_id}",
}

def get_template(notification_type: str) -> str:
    """
    指定された通知タイプのテンプレートを取得
    """
    return TEMPLATES.get(notification_type, "⚠️ 通知テンプレートが見つかりません")
