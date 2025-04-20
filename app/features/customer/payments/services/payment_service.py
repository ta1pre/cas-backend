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
import sys
from fastapi import HTTPException
from typing import Union

# --- ログ出力設定（ファイル＆コンソール） ---
root_logger = logging.getLogger()
if not root_logger.handlers:
    file_handler = logging.FileHandler('app.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s] %(message)s')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

root_logger.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
# --- ここまでログ設定 ---

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

async def create_payment_intent(db: Session, user, payment_data: CreatePaymentIntentRequest) -> str:
    from app.db.models.user import User
    try:
        # userがUser型でなければDBから取得
        if not isinstance(user, User):
            user_id = int(user) if isinstance(user, str) and str(user).isdigit() else user
            user_obj = db.query(User).filter(User.id == user_id).first()
            if not user_obj:
                logger.error(f"User not found: {user}")
                raise Exception(f"User not found: {user}")
            user = user_obj

        # ここでcustomer_idを必ず取得（無ければ自動生成＆保存）
        stripe_customer_id = await get_or_create_stripe_customer(db, user)

        intent = stripe.PaymentIntent.create(
            amount=payment_data.amount,
            currency="jpy",
            customer=stripe_customer_id,
            payment_method_types=['card', 'link'],  # Link決済を有効化
            metadata={
                'user_id': str(user.id),
                'point_value': str(payment_data.points)  # ここでポイント数も必ずセット
            }
        )
        logger.info(f"PaymentIntent created for user {user.id}: {intent.id}")
        return intent.client_secret
    except stripe.error.StripeError as e:
        logger.error(f"Stripe API error during PaymentIntent creation: {e}")
        raise
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
        payload = await request.body() if hasattr(request, 'body') else None
        logger.info(f"【DEBUG】受信payload: {payload}")
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        logger.info(f"【DEBUG】Webhook event: {event}")
        logger.info(f"【DEBUG】event type: {event.get('type') if isinstance(event, dict) else str(event)}")
        logger.info(f"Received Stripe webhook event: {event['type']}")
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid webhook payload: {e}")
        logger.exception("詳細なエラー情報:")
        return # or raise error
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid webhook signature: {e}")
        logger.exception("詳細なエラー情報:")
        return # or raise error
    except Exception as e:
        logger.error(f"Error constructing webhook event: {e}")
        logger.exception("詳細なエラー情報:")
        return

    # イベントタイプに応じて処理を分岐
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        logger.info(f"Checkout session completed: {session['id']}")
        metadata = session.get('metadata', {})
        user_id = metadata.get('user_id')
        amount = metadata.get('amount')
        if user_id is None or not amount:
            logger.error(f"ポイント付与失敗: user_idまたはamountがmetadataにありません (metadata={metadata})")
        else:
            try:
                from app.features.points.services.apply_point_rule_service import apply_point_rule
                # DBセッション取得
                from app.db.session import SessionLocal
                db = SessionLocal()
                result = apply_point_rule(db, int(user_id), 'purchase', {'amount': int(amount)})
                if result.get('success'):
                    logger.info(f"ポイント付与成功: user_id={user_id}, amount={amount}")
                else:
                    logger.error(f"ポイント付与エラー: {result.get('message')}")
            except Exception as e:
                logger.error(f"ポイント付与処理中に例外: {e}")
            finally:
                db.close()
    elif event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        logger.info(f"PaymentIntent succeeded: {payment_intent.id}")
        # ポイント付与処理はcheckout.session.completedでのみ実施
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
        # ユーザーがUser型でなければDBから取得
        from app.db.models.user import User
        if not isinstance(user, User):
            user_obj = await get_user_by_id(db, user)
        else:
            user_obj = user
        stripe_customer_id = await get_or_create_stripe_customer(db, user_obj)

        # フロントエンドのリダイレクト先URL (session_idクエリを除外)
        success_url = "http://localhost:3000/p/customer/points/success"
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
                'price_id': checkout_data.price_id,
                # ポイント購入分のamountをmetadataに必ず含める
                'amount': str(checkout_data.amount) if hasattr(checkout_data, 'amount') else ''
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
async def get_or_create_stripe_customer(db: Session, user):
    from app.db.models.user import User
    # userがUser型でなければDBから取得
    if not isinstance(user, User):
        # intまたはstr型のユーザーIDをサポート
        user_id = int(user) if isinstance(user, str) and user.isdigit() else user
        user_obj = db.query(User).filter(User.id == user_id).first()
        if not user_obj:
            logger.error(f"User not found: {user}")
            raise Exception(f"User not found: {user}")
        user = user_obj
    if user.stripe_customer_id:
        return user.stripe_customer_id
    else:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.nick_name, # ユーザー名
            description=f"user_id: {user.id}", # 管理画面で分かりやすく
            metadata={'user_id': str(user.id)} # プログラム連携用
        )
        user.stripe_customer_id = customer.id
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Stripe Customer created for user {user.id}: {customer.id}")
        return customer.id
