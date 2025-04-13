# app/features/customer/payments/endpoints/payments_routers.py
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from .payments import customer_router as customer_payment_api_router
from .payments import webhook_router as webhook_payment_api_router

# 顧客向け決済関連ルーター（認証必須）
customer_payments_router = APIRouter(
    prefix="/customer/payments",
    tags=["Customer - Payments"],
    dependencies=[Depends(get_current_user)]
)
customer_payments_router.include_router(customer_payment_api_router)

# Webhook用ルーター（認証不要）
webhook_router = APIRouter(
    prefix="/payments", # ベースパスは /api/v1/payments/webhook
    tags=["Payments - Webhook"]
    # dependencies は設定しない
)
webhook_router.include_router(webhook_payment_api_router)
