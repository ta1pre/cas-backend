# ファイル: app/features/prefecture/endpoints/prefecture.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.features.customer.area.schemas.prefecture_schema import PrefectureRegisterSchema, PrefectureSchema
from app.features.customer.area.service.prefecture_service import register_prefecture, fetch_prefectures

router = APIRouter()

@router.post("/prefectures", response_model=list[PrefectureSchema])
def get_prefectures(db: Session = Depends(get_db)):
    return fetch_prefectures(db)


# ✅ ユーザーの都道府県を登録
@router.post("/prefecture/register")
def register_user_prefecture(pref_data: PrefectureRegisterSchema, db: Session = Depends(get_db)):
    return register_prefecture(db, pref_data)