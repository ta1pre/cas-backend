# Cast Profile Repository
from sqlalchemy.orm import Session
from app.db.models.cast_common_prof import CastCommonProf
from ..schema.prof_schema import CastProfUpdate # 親ディレクトリのschemaからインポート
from typing import Optional

def get_cast_prof(db: Session, cast_id: int) -> Optional[CastCommonProf]:
    """指定された cast_id に紐づくキャストプロフィールを取得"""
    return db.query(CastCommonProf).filter(CastCommonProf.cast_id == cast_id).first()

def update_cast_prof(db: Session, cast_id: int, prof_data: CastProfUpdate) -> Optional[CastCommonProf]:
    """指定された cast_id のキャストプロフィールを更新"""
    db_prof = get_cast_prof(db, cast_id)
    if not db_prof:
        return None

    # 更新データ (Noneでない値のみ) で上書き
    update_data = prof_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_prof, key, value)

    db.commit()
    db.refresh(db_prof)
    return db_prof
