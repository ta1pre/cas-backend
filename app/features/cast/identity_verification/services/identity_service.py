from sqlalchemy.orm import Session
from app.features.cast.identity_verification.repositories.identity_repository import IdentityVerificationRepository
from app.db.models.cast_identity_verification import CastIdentityVerification
from app.db.models.media_files import MediaFile
from typing import List, Dict, Any, Optional

# u672cu4ebau78bau8a8du7533u8acbu3092u4f5cu6210u3059u308bu30b5u30fcu30d3u30b9
def create_verification_request(cast_id: int, service_type: str, id_photo_media_id: int, juminhyo_media_id: Optional[int], 
                               bank_name: Optional[str] = None, branch_name: Optional[str] = None, 
                               branch_code: Optional[str] = None, account_type: Optional[str] = None, 
                               account_number: Optional[str] = None, account_holder: Optional[str] = None, 
                               db: Session = None) -> Dict[str, Any]:
    """
    u672cu4ebau78bau8a8du7533u8acbu3092u4f5cu6210u3057u3001u7d50u679cu3092u8fd4u3059
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
        "message": "u672cu4ebau78bau8a8du7533u8acbu3092u53d7u3051u4ed8u3051u307eu3057u305fu3002u5be9u67fbu7d50u679cu3092u304au5f85u3061u304fu3060u3055u3044u3002"
    }

# u53e3u5ea7u60c5u5831u306eu307fu3092u66f4u65b0u3059u308bu30b5u30fcu30d3u30b9
def update_bank_account(cast_id: int, bank_name: str, branch_name: str, branch_code: str, 
                      account_type: str, account_number: str, account_holder: str, 
                      db: Session) -> Dict[str, Any]:
    """
    u30adu30e3u30b9u30c8u306eu53e3u5ea7u60c5u5831u306eu307fu3092u66f4u65b0u3059u308b
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
        "message": "u53e3u5ea7u60c5u5831u304cu6b63u5e38u306bu66f4u65b0u3055u308cu307eu3057u305fu3002"
    }

# u672cu4ebau78bau8a8du30b9u30c6u30fcu30bfu30b9u3092u53d6u5f97u3059u308bu30b5u30fcu30d3u30b9
def get_verification_status(cast_id: int, db: Session) -> Dict[str, Any]:
    """
    u30adu30e3u30b9u30c8u306eu672cu4ebau78bau8a8du30b9u30c6u30fcu30bfu30b9u3092u53d6u5f97
    """
    repo = IdentityVerificationRepository(db)
    verification = repo.get_verification_status(cast_id)
    
    if not verification:
        return {
            "cast_id": cast_id,
            "status": "unsubmitted",
            "message": "u672cu4ebau78bau8a8du7533u8acbu304cu307eu3060u884cu308fu308cu3066u3044u307eu305bu3093u3002"
        }
    
    # u30b9u30c6u30fcu30bfu30b9u306bu5fdcu3058u305fu30e1u30c3u30bbu30fcu30b8u3092u8a2du5b9a
    message = ""
    if verification.status == "pending":
        message = "u672cu4ebau78bau8a8du7533u8acbu3092u53d7u3051u4ed8u3051u307eu3057u305fu3002u5be9u67fbu7d50u679cu3092u304au5f85u3061u304fu3060u3055u3044u3002"
    elif verification.status == "approved":
        message = "u672cu4ebau78bau8a8du304cu5b8cu4e86u3057u307eu3057u305fu3002"
    elif verification.status == "rejected":
        message = f"u672cu4ebau78bau8a8du304cu5374u4e0bu3055u308cu307eu3057u305fu3002u7406u7531: {verification.rejection_reason or 'u8a73u7d30u306au7406u7531u306fu8a18u8f09u3055u308cu3066u3044u307eu305bu3093'}"
    
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

# u7ba1u7406u8005u304cu672cu4ebau78bau8a8du3092u5be9u67fbu3059u308bu30b5u30fcu30d3u30b9
def review_verification(cast_id: int, status: str, reviewer_id: int, rejection_reason: Optional[str], db: Session) -> Dict[str, Any]:
    """
    u7ba1u7406u8005u304cu672cu4ebau78bau8a8du3092u5be9u67fbu3057u3001u7d50u679cu3092u66f4u65b0u3059u308b
    """
    repo = IdentityVerificationRepository(db)
    verification = repo.update_verification_status(cast_id, status, reviewer_id, rejection_reason)
    
    message = "u5be9u67fbu304cu5b8cu4e86u3057u307eu3057u305fu3002"
    if status == "approved":
        message = "u672cu4ebau78bau8a8du3092u627fu8a8du3057u307eu3057u305fu3002"
    elif status == "rejected":
        message = f"u672cu4ebau78bau8a8du3092u5374u4e0bu3057u307eu3057u305fu3002u7406u7531: {verification.rejection_reason or 'u8a73u7d30u306au7406u7531u306fu8a18u8f09u3055u308cu3066u3044u307eu305bu3093'}"
    
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

# u672cu4ebau78bau8a8du66f8u985eu3092u53d6u5f97u3059u308bu30b5u30fcu30d3u30b9
def get_verification_documents(cast_id: int, db: Session) -> List[Dict[str, Any]]:
    """
    u30adu30e3u30b9u30c8u306eu672cu4ebau78bau8a8du66f8u985eu3092u53d6u5f97
    """
    repo = IdentityVerificationRepository(db)
    documents = repo.get_verification_documents(cast_id)
    
    result = []
    for doc in documents:
        doc_type = "u5199u771fu4ed8u304du8eabu5206u8a3cu660eu66f8" if doc.order_index == 0 else "u4f4fu6c11u7968"
        result.append({
            "document_type": doc_type,
            "file_url": doc.file_url,
            "order_index": doc.order_index,
            "file_type": doc.file_type
        })
    
    return result
