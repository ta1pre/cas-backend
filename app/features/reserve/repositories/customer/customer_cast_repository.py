# app/features/reserve/repositories/customer/customer_cast_repository.py
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.db.models.cast_common_prof import CastCommonProf
from app.features.customer.castprof.repositories.image_repository import get_cast_images

def get_customer_cast_profile(cast_id: int, db: Session):
    """カスタマー向けのキャスト基本情報を取得"""
    # 名前を取得
    stmt = select(CastCommonProf.cast_id, CastCommonProf.name).where(CastCommonProf.cast_id == cast_id)
    result = db.execute(stmt).first()

    if not result:
        return None

    # 画像を取得（order_index = 0 のものを `profile_image_url` とする）
    images = get_cast_images(cast_id, db)
    profile_image_url = images[0]["url"] if images else None

    return {
        "cast_id": result.cast_id,
        "name": result.name,
        "profile_image_url": profile_image_url
    }
