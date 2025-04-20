# app/features/customer/payments/schemas/payment_schema.py
from pydantic import BaseModel, Field

class CreatePaymentIntentRequest(BaseModel):
    amount: int
    points: int # 購入ポイント数（P）
    currency: str = "jpy" # デフォルトは円
    # 必要に応じて他の情報（商品IDなど）を追加

class CreatePaymentIntentResponse(BaseModel):
    client_secret: str

# --- ここから追加 ---
class CreateCheckoutSessionRequest(BaseModel):
    price_id: str = Field(..., description="Stripeの商品価格ID")
    # 必要に応じて数量なども追加可能
    # quantity: int = Field(1, gt=0, description="数量")

class CreateCheckoutSessionResponse(BaseModel):
    checkout_url: str = Field(..., description="Stripe CheckoutページのURL")
# --- ここまで追加 ---
