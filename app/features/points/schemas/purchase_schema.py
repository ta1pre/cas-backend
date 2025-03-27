# app/features/points/schemas/purchase_schema.py

from pydantic import BaseModel

class PurchasePointRequest(BaseModel):
    user_id: int
    amount: int

class PurchasePointResponse(BaseModel):
    message: str
    new_balance: int
