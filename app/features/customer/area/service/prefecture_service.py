# ファイル: app/services/prefecture_service.py

from sqlalchemy.orm import Session
from app.db.models.user import User
from app.features.customer.area.repositories.prefecture_repository import get_all_prefectures
from app.features.customer.area.schemas.prefecture_schema import PrefectureRegisterSchema

def fetch_prefectures(db: Session):
    return get_all_prefectures(db)

def register_prefecture(db: Session, pref_data: PrefectureRegisterSchema):
    user = db.query(User).filter(User.id == pref_data.user_id).first()
    if not user:
        return {"error": "User not found"}

    user.prefectures = str(pref_data.prefecture_id)  # ✅ ユーザーの都道府県を登録
    db.commit()
    return {"message": "Prefecture updated successfully"}