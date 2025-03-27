# app/features/customer/castprof/repositories/image_repository.py
from sqlalchemy.orm import aliased, Session
from sqlalchemy.future import select
from app.db.models.media_files import MediaFile

def get_cast_images(cast_id: int, db: Session):
    """キャストの画像リストを取得"""
    MediaAlias = aliased(MediaFile)

    stmt = (
        select(MediaAlias.file_url, MediaAlias.order_index)
        .where((MediaAlias.target_id == cast_id) & (MediaAlias.target_type == "profile_common"))
        .order_by(MediaAlias.order_index)
    )

    result = db.execute(stmt).all()

    return [{"url": row.file_url, "order_index": row.order_index} for row in result if row.file_url]
