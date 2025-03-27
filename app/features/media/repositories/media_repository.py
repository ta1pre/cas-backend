from sqlalchemy.orm import Session
from app.db.models.media_files import MediaFile

# ✅ メディアファイルの登録
def save_media_info(file_url: str, file_type: str, target_type: str, target_id: int, order_index: int, db: Session):
    media = MediaFile(
        file_url=file_url,
        file_type=file_type,
        target_type=target_type,
        target_id=target_id,
        order_index=order_index
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


#削除
def delete_media_records(db: Session, target_type: str, target_id: int, order_index: int) -> bool:
    """DB から `target_type` / `target_id` / `order_index` に該当するレコードを削除"""
    media_files = db.query(MediaFile).filter(
        MediaFile.target_type == target_type,
        MediaFile.target_id == target_id,
        MediaFile.order_index == order_index
    ).all()

    if not media_files:
        print("[INFO] ℹ️ 削除対象のメディアなし")
        return False

    print(f"[INFO] 🗑️ DB から削除対象のメディア {len(media_files)} 件")

    for media in media_files:
        print(f"[INFO] 🗑️ DB から削除: {media.file_url}")
        db.delete(media)
    
    db.commit()
    print("[INFO] ✅ DB からメディア削除成功")
    return True