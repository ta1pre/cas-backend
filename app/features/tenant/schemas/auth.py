from pydantic import BaseModel, EmailStr

class TenantLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TenantLoginResponse(BaseModel):
    access_token: str
    refresh_token: str  # リフレッシュトークンを追加
    token_type: str = "bearer"
