from pydantic import BaseModel, EmailStr

class TenantLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TenantLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
