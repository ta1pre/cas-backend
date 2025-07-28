from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# 本人確認申請リクエスト（口座関連フィールドを削除）
class IdentityVerificationRequest(BaseModel):
    cast_id: Optional[int] = Field(None, description="キャストID（指定しない場合は認証済みユーザーのIDが使用されます）")
    service_type: str = Field(..., description="サービス種別 (A: 通常サービス, B: 風俗関連サービス)")
    id_photo_media_id: int = Field(..., description="身分証明書のメディアID")
    juminhyo_media_id: Optional[int] = Field(None, description="住民票のメディアID（風俗関連サービスの場合は必須）")
    document_type: Optional[str] = Field(None, description="身分証の種類")

# 基本身分証アップロードリクエスト
class BasicDocumentUploadRequest(BaseModel):
    id_photo_media_id: int = Field(..., description="身分証明書のメディアID")
    document_type: str = Field(..., description="身分証の種類（license, mynumber, passport, basic_resident_card）")

# 住民票アップロードリクエスト
class ResidenceDocumentUploadRequest(BaseModel):
    juminhyo_media_id: int = Field(..., description="住民票のメディアID")

# 本人確認レスポンス（口座関連フィールドを削除）
class IdentityVerificationResponse(BaseModel):
    cast_id: int
    status: str
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    document_type: Optional[str] = None
    success: Optional[bool] = True
    message: Optional[str] = None

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

# アップロード進捗レスポンス
class DocumentUploadStatus(BaseModel):
    uploaded: bool
    uploaded_at: Optional[str] = None
    file_name: Optional[str] = None

class UploadProgressResponse(BaseModel):
    status: str = Field(..., description="全体のステータス")
    progress: dict = Field(..., description="進捗情報")
    completion_rate: int = Field(..., description="完了率（0-100）")
    current_step: str = Field(..., description="現在のステップ")
    next_action: Optional[str] = Field(None, description="次のアクション")