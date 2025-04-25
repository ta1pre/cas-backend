# テナント作成用リクエスト・レスポンススキーマ
from pydantic import BaseModel, EmailStr, constr

class TenantCreateRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    nick_name: str

class TenantCreateResponse(BaseModel):
    user_id: int
    email: EmailStr
    status: str
