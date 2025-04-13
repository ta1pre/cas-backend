# app/features/customer/payments/endpoints/payments.py
from fastapi import APIRouter, Depends, Request, Response, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.db.models.user import User
from app.features.customer.payments.schemas import payment_schema
from app.features.customer.payments.services import payment_service
import logging

logger = logging.getLogger(__name__)

# 
customer_router = APIRouter()

# Webhook
webhook_router = APIRouter()

@customer_router.post(
    "/create-payment-intent",
    response_model=payment_schema.CreatePaymentIntentResponse,
    summary="Create Stripe Payment Intent",
    description=""
)
async def create_payment_intent_endpoint(
    payment_data: payment_schema.CreatePaymentIntentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    PaymentIntentclient_secret
    """
    try:
        client_secret = await payment_service.create_payment_intent(
            db=db, user=current_user, payment_data=payment_data
        )
        return payment_schema.CreatePaymentIntentResponse(client_secret=client_secret)
    except Exception as e:
        logger.error(f"Error creating PaymentIntent for user {current_user}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="決済情報の作成に失敗しました。")


@webhook_router.post(
    "/webhook",
    summary="Stripe Webhook Endpoint",
    description="Stripe",
    status_code=200 # Stripe200 OK
)
async def stripe_webhook(
    request: Request,
    # Stripe raw bytes 
    # payload: bytes = Body(...)
):
    """
    StripeWebhook
    """
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    if not sig_header:
        logger.warning("Missing Stripe-Signature header in webhook request.")
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    try:
        await payment_service.handle_webhook_event(payload.decode('utf-8'), sig_header)
    except HTTPException as http_exc:
        # handle_webhook_eventHTTPException
        raise http_exc
    except Exception as e:
        # 
        logger.error(f"Unhandled error processing Stripe webhook: {e}", exc_info=True)
        # Stripe Stripe
        # 500 
        # raise HTTPException(status_code=500, detail="Internal server error")
        pass # 

    # Stripe200 OK
    return Response(status_code=200)
