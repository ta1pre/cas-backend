from sqlalchemy.orm import Session
from app.features.media.repositories.media_repository import save_media_info
from app.features.media.services.s3_service import generate_presigned_url
from app.db.models.media_files import MediaFile

# ✅ 署名付きURLを取得
def get_presigned_url(file_name: str, file_type: str, target_type: str, target_id: int, order_index: int):
    return generate_presigned_url(file_name, file_type, target_type, target_id, order_index)

# ✅ DB にアップロード情報を保存
def save_uploaded_file_info(file_url: str, file_type: str, target_type: str, target_id: int, order_index: int, db: Session):
    """
    S3 にアップロードされたファイル情報を DB に保存
    """
    try:
        save_media_info(file_url, file_type, target_type, target_id, order_index, db)
        print(f"[INFO] ✅ ファイル情報を DB に保存: {file_url}")
        return True
    except Exception as e:
        print(f"[ERROR] DB への保存に失敗: {str(e)}")
        return False
    
