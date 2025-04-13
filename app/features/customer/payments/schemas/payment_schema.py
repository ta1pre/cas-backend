# app/features/customer/payments/schemas/payment_schema.py
from pydantic import BaseModel

class CreatePaymentIntentRequest(BaseModel):
    amount: int
    currency: str = "jpy" # デフォルトは円
    # 必要に応じて他の情報（商品IDなど）を追加

class CreatePaymentIntentResponse(BaseModel):
    client_secret: str
