# ファイル: app/repositories/prefecture_repository.py

from sqlalchemy.orm import Session
from app.db.models.prefectures import Prefecture

def get_all_prefectures(db: Session):
    return db.query(Prefecture).all()
