# ✅ media_schema.py - リクエスト・レスポンススキーマ
from pydantic import BaseModel, Field

class MediaUploadRequest(BaseModel):
    file_name: str = Field(..., example="profile_image.jpg")
    file_type: str = Field(..., example="image/jpeg")
    target_type: str = Field(..., example="profile_common")
    target_id: int = Field(..., example=41)
    order_index: int = Field(..., example=0)# ✅ リクエスト用スキーマ

# /get-by-indexで使用
class GetMediaRequest(BaseModel):
    target_type: str = Field(..., example="profile_common")
    target_id: int = Field(..., example=42)
    order_index: int = Field(..., example=2)

# ✅ `register` API 用のリクエストスキーマ
class RegisterMediaRequest(BaseModel):
    file_url: str = Field(..., example="https://s3.amazonaws.com/.../profile_common/42/2/image_1700000000.jpg")
    file_type: str = Field(..., example="image/jpeg")
    target_type: str = Field(..., example="profile_common")
    target_id: int = Field(..., example=42)
    order_index: int = Field(..., example=2)
    
from pydantic import BaseModel, Field

# ✅ `delete` API のリクエストスキーマ
class MediaDeleteRequest(BaseModel):
    target_type: str = Field(..., example="profile_common")
    target_id: int = Field(..., example=42)
    order_index: int = Field(..., example=0)


