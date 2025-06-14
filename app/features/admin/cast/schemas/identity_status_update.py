from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Literal

class CastIdentityStatusUpdateRequest(BaseModel):
    """リクエスト: キャスト本人確認ステータス更新"""

    status: Literal["approved", "rejected", "pending"] = Field(..., description="更新後ステータス")
    rejection_reason: Optional[str] = Field(None, description="却下理由（rejected の場合のみ必須）")


class CastIdentityStatusUpdateResponse(BaseModel):
    """レスポンス: 更新結果"""

    cast_id: int
    status: str
    message: str = "updated"  
