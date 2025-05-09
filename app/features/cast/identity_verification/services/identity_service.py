from sqlalchemy.orm import Session
from app.features.cast.identity_verification.repositories.identity_repository import IdentityVerificationRepository
from app.db.models.cast_identity_verification import CastIdentityVerification
from app.db.models.media_files import MediaFile
from typing import List, Dict, Any, Optional

# 本人確認申請を作成するサービス
def create_verification_request(cast_id: int, service_type: str, id_photo_media_id: int, juminhyo_media_id: Optional[int], 
                               bank_name: Optional[str] = None, branch_name: Optional[str] = None, 
                               branch_code: Optional[str] = None, account_type: Optional[str] = None, 
                               account_number: Optional[str] = None, account_holder: Optional[str] = None, 
                               db: Session = None) -> Dict[str, Any]:
    """
    本人確認申請を作成し、結果を返す
    """
    repo = IdentityVerificationRepository(db)
    verification = repo.create_verification_request(
        cast_id, service_type, id_photo_media_id, juminhyo_media_id,
        bank_name, branch_name, branch_code, account_type, account_number, account_holder
    )
    
    return {
        "cast_id": verification.cast_id,
        "status": verification.status,
        "submitted_at": verification.submitted_at,
        "message": "本人確認申請を作成しました。後日結果を確認してください。"
    }

# 銀行口座情報を更新するサービス
def update_bank_account(cast_id: int, bank_name: str, branch_name: str, branch_code: str, 
                      account_type: str, account_number: str, account_holder: str, 
                      db: Session) -> Dict[str, Any]:
    """
    本人確認申請中の銀行口座情報を更新する
    """
    repo = IdentityVerificationRepository(db)
    verification = repo.update_bank_account(
        cast_id, bank_name, branch_name, branch_code, 
        account_type, account_number, account_holder
    )
    
    return {
        "cast_id": verification.cast_id,
        "status": verification.status,
        "bank_name": verification.bank_name,
        "branch_name": verification.branch_name,
        "branch_code": verification.branch_code,
        "account_type": verification.account_type,
        "account_number": verification.account_number,
        "account_holder": verification.account_holder,
        "message": "銀行口座情報を更新しました。"
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
        "bank_name": verification.bank_name,
        "branch_name": verification.branch_name,
        "branch_code": verification.branch_code,
        "account_type": verification.account_type,
        "account_number": verification.account_number,
        "account_holder": verification.account_holder,
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
        "bank_name": verification.bank_name,
        "branch_name": verification.branch_name,
        "branch_code": verification.branch_code,
        "account_type": verification.account_type,
        "account_number": verification.account_number,
        "account_holder": verification.account_holder,
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
