from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# 本人確認申請リクエスト
class IdentityVerificationRequest(BaseModel):
    cast_id: Optional[int] = Field(None, description="キャストID（指定しない場合は認証済みユーザーのIDが使用されます）")
    service_type: str = Field(..., description="サービス種別 (A: 通常サービス, B: 風俗関連サービス)")
    id_photo_media_id: int = Field(..., description="身分証明書のメディアID")
    juminhyo_media_id: Optional[int] = Field(None, description="住民票のメディアID（風俗関連サービスの場合は必須）")

# 本人確認レスポンス
class IdentityVerificationResponse(BaseModel):
    cast_id: int
    status: str
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

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
