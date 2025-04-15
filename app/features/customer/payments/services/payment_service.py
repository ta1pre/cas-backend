# app/features/customer/payments/services/payment_service.py
import stripe
from app.core import config
from app.db.models.user import User
from app.features.customer.payments.schemas.payment_schema import (
    CreatePaymentIntentRequest,
    CreateCheckoutSessionRequest,
    CreateCheckoutSessionResponse
)
from sqlalchemy.orm import Session
import logging
from fastapi import HTTPException
from typing import Union

logger = logging.getLogger(__name__)

# Stripe APIキーを設定
stripe.api_key = config.STRIPE_SECRET_KEY

# ユーザーIDからユーザーオブジェクトを取得する関数
async def get_user_by_id(db: Session, user_id: int) -> User:
    """
    ユーザーIDからユーザーオブジェクトを取得する
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise ValueError(f"User with ID {user_id} not found")
    return user

async def create_payment_intent(db: Session, user: User, payment_data: CreatePaymentIntentRequest) -> str:
    """
    Stripe PaymentIntent を作成し、client_secret を返す
    """
    try:
        # ユーザーに紐づくStripe Customer IDを取得または作成
        user_obj = user if not isinstance(user, int) else await get_user_by_id(db, user)
        stripe_customer_id = await get_or_create_stripe_customer(db, user_obj)

        # user ID と user オブジェクトを処理
        user_id = user if isinstance(user, int) else user.id

        intent = stripe.PaymentIntent.create(
            amount=payment_data.amount,
            currency=payment_data.currency,
            customer=stripe_customer_id, # 顧客IDを紐付ける
            # payment_method_types=["card"], # 必要に応じて支払い方法を指定
            metadata={'user_id': str(user_id)} # ユーザーIDなどをメタデータに含める
        )
        logger.info(f"PaymentIntent created for user {user_id}: {intent.id}")
        return intent.client_secret
    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error during PaymentIntent creation: {e}")
        raise # エラーを上位に伝播させるか、適切なエラーハンドリング
    except Exception as e:
        logger.error(f"Unexpected error during PaymentIntent creation: {e}")
        raise

async def handle_webhook_event(payload: str, sig_header: str):
    """
    Stripe Webhook イベントを処理する
    """
    event = None
    webhook_secret = config.STRIPE_WEBHOOK_SECRET

    if not webhook_secret:
        logger.error("Stripe Webhook secret is not configured.")
        # 適切なエラー処理 (例: HTTPException)
        return

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        logger.info(f"Received Stripe webhook event: {event['type']}")
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid webhook payload: {e}")
        # raise HTTPException(status_code=400, detail="Invalid payload")
        return # or raise error
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid webhook signature: {e}")
        # raise HTTPException(status_code=400, detail="Invalid signature")
        return # or raise error
    except Exception as e:
        logger.error(f"Error constructing webhook event: {e}")
        # raise HTTPException(status_code=500, detail="Internal server error")
        return

    # イベントタイプに応じて処理を分岐
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        logger.info(f"PaymentIntent succeeded: {payment_intent.id}")
        # TODO: 支払い成功時の処理（DB更新、通知など）
        # user_id = payment_intent['metadata'].get('user_id')
        # amount = payment_intent['amount']
        # update_order_status(user_id, payment_intent.id, 'paid')

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        logger.warning(f"PaymentIntent failed: {payment_intent.id}")
        # TODO: 支払い失敗時の処理

    # 他のイベントタイプも必要に応じて追加
    # elif event['type'] == 'charge.succeeded':
    #     charge = event['data']['object']
    #     # ...

    else:
        logger.info(f"Unhandled webhook event type: {event['type']}")

    # Stripeに受信成功を通知
    return

async def create_checkout_session(db: Session, user: Union[User, int], checkout_data: CreateCheckoutSessionRequest) -> str:
    """
    Stripe Checkout Session を作成し、そのURLを返す
    user: User または user_id (int) を許容
    """
    try:
        # ユーザーがint型ならDBから取得
        user_obj = user if not isinstance(user, int) else await get_user_by_id(db, user)
        stripe_customer_id = await get_or_create_stripe_customer(db, user_obj)

        # フロントエンドのリダイレクト先URL (環境変数などから取得するのが望ましい)
        success_url = "http://localhost:3000/p/customer/points/success?session_id={CHECKOUT_SESSION_ID}"
        cancel_url = "http://localhost:3000/p/customer/points/cancel"

        checkout_session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': checkout_data.price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': str(user_obj.id),
                'price_id': checkout_data.price_id
            }
        )
        logger.info(f"Checkout Session created for user {user_obj.id}: {checkout_session.id}")
        return checkout_session.url

    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error during Checkout Session creation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="決済セッションの作成に失敗しました。")
    except Exception as e:
        logger.error(f"Unexpected error during Checkout Session creation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="予期せぬエラーが発生しました。")

# Stripe Customer を管理する関数
async def get_or_create_stripe_customer(db: Session, user: User) -> str:
    if user.stripe_customer_id:
        return user.stripe_customer_id
    else:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.nick_name, # ユーザー名など
            metadata={'user_id': str(user.id)}
        )
        user.stripe_customer_id = customer.id
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Stripe Customer created for user {user.id}: {customer.id}")
        return customer.id
