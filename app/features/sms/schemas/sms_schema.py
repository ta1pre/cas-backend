from pydantic import BaseModel, Field

class SendCodeRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+81\d{9,10}$")  # 日本の電話番号形式

class VerifyCodeRequest(BaseModel):
    code: str = Field(..., min_length=4, max_length=4)  # 認証コード（4桁）
