from pydantic import BaseModel, Field
from typing import Optional

# ✅ JWTトークン
class Token(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUz...")
    token_type: str = Field(..., example="bearer")


# ✅ トークンデータ
class TokenData(BaseModel):
    line_id: Optional[str] = None
    user_id: Optional[int] = None
    user_type: Optional[str] = None
