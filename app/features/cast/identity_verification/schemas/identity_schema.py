from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# 本人確認申請リクエスト
class IdentityVerificationRequest(BaseModel):
    cast_id: Optional[int] = Field(None, description="キャストID（指定しない場合は認証済みユーザーのIDが使用されます）")
    service_type: str = Field(..., description="サービス種別 (A: 通常サービス, B: 風俗関連サービス)")
    id_photo_media_id: int = Field(..., description="身分証明書のメディアID")
    juminhyo_media_id: Optional[int] = Field(None, description="住民票のメディアID（風俗関連サービスの場合は必須）")
    
    # 口座情報フィールド
    bank_name: Optional[str] = Field(None, description="銀行名（例：みずほ銀行）")
    branch_name: Optional[str] = Field(None, description="支店名（例：渋谷支店）")
    branch_code: Optional[str] = Field(None, description="支店コード（3桁、例：123）")
    account_type: Optional[str] = Field(None, description="口座種別（例：普通）")
    account_number: Optional[str] = Field(None, description="口座番号（例：1234567）")
    account_holder: Optional[str] = Field(None, description="口座名義人（例：ヤマダ タロウ）")

# 口座情報更新リクエスト
class BankAccountUpdateRequest(BaseModel):
    cast_id: Optional[int] = Field(None, description="キャストID（指定しない場合は認証済みユーザーのIDが使用されます）")
    bank_name: str = Field(..., description="銀行名（例：みずほ銀行）")
    branch_name: str = Field(..., description="支店名（例：渋谷支店）")
    branch_code: str = Field(..., description="支店コード（3桁、例：123）")
    account_type: str = Field(..., description="口座種別（例：普通）")
    account_number: str = Field(..., description="口座番号（例：1234567）")
    account_holder: str = Field(..., description="口座名義人（例：ヤマダ タロウ）")

# 本人確認レスポンス
class IdentityVerificationResponse(BaseModel):
    cast_id: int
    status: str
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # 口座情報フィールド
    bank_name: Optional[str] = None
    branch_name: Optional[str] = None
    branch_code: Optional[str] = None
    account_type: Optional[str] = None
    account_number: Optional[str] = None
    account_holder: Optional[str] = None

# 管理者による本人確認申請レスポンス
class ReviewVerificationRequest(BaseModel):
    cast_id: int
    status: str = Field(..., description="審査結果: 'approved' または 'rejected'")
    reviewer_id: int
    rejection_reason: Optional[str] = None

# 本人確認書類レスポンス
class IdentityDocumentResponse(BaseModel):
    document_type: str
    file_url: str

# 本人確認書類リストレスポンス
class IdentityDocumentsResponse(BaseModel):
    documents: List[IdentityDocumentResponse]
