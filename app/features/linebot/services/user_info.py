from sqlalchemy.orm import Session
from app.features.linebot.repositories.user_repository import LinebotUserRepository

def fetch_user_info_by_line_id(db: Session, line_id: str) -> dict:
    """
    データベースからLINE IDを使用してユーザー情報を取得
    """
    repository = LinebotUserRepository(db)
    user = repository.get_user_by_line_id(line_id)
    
    if user:
        return {
            "id": user.id,
            "nickname": user.nick_name or "ゲスト",
            "type": user.user_type or "common",
            "last_login": user.last_login or "未ログイン",
            "sex": user.sex or "未設定",
            "birth": user.birth or "未設定"
        }
    else:
        return {
            "id": None,
            "nickname": "ゲスト",
            "type": "common",
            "last_login": "未ログイン",
            "sex": "未設定",
            "birth": "未設定"
        }
