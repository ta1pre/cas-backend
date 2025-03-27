from pydantic import BaseModel, Field

# ✅ SMS認証コード送信用モデル
class PhoneVerificationRequest(BaseModel):
    mobile_phone: str = Field(..., example="09012345678")


# ✅ SMS認証コード確認用モデル
class PhoneVerificationCode(BaseModel):
    mobile_phone: str = Field(..., example="09012345678")
    code: str = Field(..., example="1234")
