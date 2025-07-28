from sqlalchemy.orm import Session
from app.features.cast.identity_verification.repositories.identity_repository import IdentityVerificationRepository
from app.db.models.cast_identity_verification import CastIdentityVerification
from app.db.models.media_files import MediaFile
from typing import List, Dict, Any, Optional

# 本人確認申請を作成するサービス（口座関連パラメータを削除）
def create_verification_request(cast_id: int, service_type: str, id_photo_media_id: int, juminhyo_media_id: Optional[int], 
                               document_type: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
    """
    本人確認申請を作成し、結果を返す（口座情報は削除）
    """
    repo = IdentityVerificationRepository(db)
    verification = repo.create_verification_request(
        cast_id, service_type, id_photo_media_id, juminhyo_media_id, document_type
    )
    
    return {
        "cast_id": verification.cast_id,
        "status": verification.status,
        "submitted_at": verification.submitted_at,
        "document_type": verification.document_type,
        "message": "本人確認申請を作成しました。後日結果を確認してください。"
    }

# 基本身分証をアップロードするサービス
def upload_basic_document(cast_id: int, id_photo_media_id: int, document_type: str, db: Session) -> Dict[str, Any]:
    """
    基本身分証をアップロードする
    """
    repo = IdentityVerificationRepository(db)
    verification = repo.upload_basic_document(cast_id, id_photo_media_id, document_type)
    
    return {
        "cast_id": verification.cast_id,
        "status": verification.status,
        "document_type": verification.document_type,
        "success": True,
        "message": "基本身分証のアップロードが完了しました。"
    }

# 住民票をアップロードするサービス
def upload_residence_document(cast_id: int, juminhyo_media_id: int, db: Session) -> Dict[str, Any]:
    """
    住民票をアップロードする
    """
    repo = IdentityVerificationRepository(db)
    verification = repo.upload_residence_document(cast_id, juminhyo_media_id)
    
    return {
        "cast_id": verification.cast_id,
        "status": verification.status,
        "success": True,
        "message": "住民票のアップロードが完了しました。"
    }

# アップロード進捗を取得するサービス
def get_upload_progress(cast_id: int, db: Session) -> Dict[str, Any]:
    """
    アップロード進捗を取得する
    """
    repo = IdentityVerificationRepository(db)
    verification = repo.get_verification_status(cast_id)
    
    # 基本身分証のアップロード状況
    basic_uploaded = verification and verification.id_photo_media_id is not None
    # 住民票のアップロード状況
    residence_uploaded = verification and verification.juminhyo_media_id is not None
    
    # 完了率計算
    completion_rate = 0
    if basic_uploaded:
        completion_rate += 50
    if residence_uploaded:
        completion_rate += 50
    
    # 現在のステップ判定
    if not basic_uploaded:
        current_step = "basic"
        next_action = "基本身分証をアップロードしてください"
    elif not residence_uploaded:
        current_step = "residence"
        next_action = "住民票をアップロードしてください"
    else:
        current_step = "review"
        next_action = None
    
    # 全体ステータス判定
    if verification and verification.status == "pending":
        status = "pending"
    elif verification and verification.status == "approved":
        status = "approved"
    elif verification and verification.status == "rejected":
        status = "rejected"
    else:
        status = "unsubmitted"
    
    return {
        "status": status,
        "progress": {
            "basic_document": {
                "uploaded": basic_uploaded,
                "uploaded_at": verification.submitted_at.isoformat() if verification and verification.submitted_at else None,
                "file_name": f"基本身分証_{verification.document_type}" if verification and verification.document_type else None
            },
            "residence_document": {
                "uploaded": residence_uploaded,
                "uploaded_at": verification.submitted_at.isoformat() if verification and verification.submitted_at else None,
                "file_name": "住民票" if residence_uploaded else None
            }
        },
        "completion_rate": completion_rate,
        "current_step": current_step,
        "next_action": next_action
    }

# 本人確認ステータスを取得するサービス
def get_verification_status(cast_id: int, db: Session) -> Dict[str, Any]:
    """
    キャストの本人確認ステータスを取得
    """
    print(f"[DEBUG] Received cast_id: {cast_id}, type: {type(cast_id)}")  # デバッグログ
    
    # cast_idがUserオブジェクトの場合に備えて処理
    actual_cast_id = cast_id.id if hasattr(cast_id, 'id') else cast_id
    print(f"[DEBUG] Using cast_id: {actual_cast_id}")  # デバッグログ
    
    repo = IdentityVerificationRepository(db)
    verification = repo.get_verification_status(actual_cast_id)
    
    if not verification:
        return {
            "cast_id": actual_cast_id,
            "status": "unsubmitted",
            "message": "本人確認申請がまだ行われていません。"
        }
    
    # ステータスメッセージを設定
    message = ""
    if verification.status == "pending":
        message = "本人確認申請を作成しました。後日結果を確認してください。"
    elif verification.status == "approved":
        message = "本人確認が承認されました。"
    elif verification.status == "rejected":
        message = f"本人確認が却下されました。理由: {verification.rejection_reason or '不明な理由で却下されました'}"
    
    return {
        "cast_id": verification.cast_id,
        "status": verification.status,
        "submitted_at": verification.submitted_at,
        "reviewed_at": verification.reviewed_at,
        "rejection_reason": verification.rejection_reason,
        "document_type": verification.document_type,
        "message": message
    }

# 管理者が本人確認を審査するサービス
def review_verification(cast_id: int, status: str, reviewer_id: int, rejection_reason: Optional[str], db: Session) -> Dict[str, Any]:
    """
    管理者が本人確認を審査し、結果を更新する
    """
    repo = IdentityVerificationRepository(db)
    verification = repo.update_verification_status(cast_id, status, reviewer_id, rejection_reason)
    
    message = "審査結果を更新しました。"
    if status == "approved":
        message = "本人確認を承認しました。"
    elif status == "rejected":
        message = f"本人確認を却下しました。理由: {verification.rejection_reason or '不明な理由で却下されました'}"
    
    return {
        "cast_id": verification.cast_id,
        "status": verification.status,
        "submitted_at": verification.submitted_at,
        "reviewed_at": verification.reviewed_at,
        "rejection_reason": verification.rejection_reason,
        "document_type": verification.document_type,
        "message": message
    }

# 本人確認書類を取得するサービス
def get_verification_documents(cast_id: int, db: Session) -> List[Dict[str, Any]]:
    """
    キャストの本人確認書類を取得
    """
    repo = IdentityVerificationRepository(db)
    documents = repo.get_verification_documents(cast_id)
    
    result = []
    for doc in documents:
        doc_type = "身分証明書" if doc.order_index == 0 else "住民票"
        result.append({
            "document_type": doc_type,
            "file_url": doc.file_url,
            "order_index": doc.order_index,
            "file_type": doc.file_type
        })
    
    return result
