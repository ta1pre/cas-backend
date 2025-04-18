# app/features/customer/payments/endpoints/payments.py
from fastapi import APIRouter, Depends, Request, Response, HTTPException, Body, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.db.models.user import User
from app.features.customer.payments.schemas import payment_schema
from app.features.customer.payments.schemas.payment_schema import (
    CreateCheckoutSessionRequest,
    CreateCheckoutSessionResponse
)
from app.features.customer.payments.services import payment_service
import logging
from app.core.config import STRIPE_WEBHOOK_SECRET
import json
import stripe

# ロガーの設定
logger = logging.getLogger(__name__)

# Webhook用のシークレットキーを直接指定
WEBHOOK_SECRET = STRIPE_WEBHOOK_SECRET

# 
customer_router = APIRouter() # 顧客向けエンドポイント用
webhook_router = APIRouter() # Webhook用

# Webhook
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


@customer_router.post(
    "/create-checkout-session",
    response_model=CreateCheckoutSessionResponse,
    summary="Create Stripe Checkout Session",
    description="指定された価格IDに基づいてStripe Checkoutセッションを作成し、そのURLを返します。"
)
async def create_checkout_session_endpoint(
    checkout_data: CreateCheckoutSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Stripe Checkout Sessionを作成し、決済ページのURLを返す。
    """
    try:
        checkout_url = await payment_service.create_checkout_session(
            db=db, user=current_user, checkout_data=checkout_data
        )
        return CreateCheckoutSessionResponse(checkout_url=checkout_url)
    except HTTPException as http_exc:
        # サービス層からのHTTPExceptionはそのまま再raise
        raise http_exc
    except Exception as e:
        # 予期せぬエラー
        logger.error(f"Error creating Checkout Session for user {current_user}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="決済セッションの作成中に予期せぬエラーが発生しました。")


@webhook_router.post(
    "/webhook",
    summary="Stripe Webhook Endpoint",
    description="StripeからのWebhookイベントを受信します。",
    status_code=200, # Stripeは成功時に200 OKを期待
    response_class=Response, # レスポンスクラスを指定してCORS対応
    dependencies=[] # 依存関係を空にしてミドルウェアをスキップ
)
async def stripe_webhook(request: Request, stripe_signature: str = Header(None, alias="stripe-signature"), db: Session = Depends(get_db)):
    logger.info("Webhook received") # INFOレベルで受信ログ

    try:
        # リクエストボディを読み取る
        payload = await request.body()
        logger.debug(f"Received payload (first 100 bytes): {payload[:100]}...")

        # Stripe-Signatureヘッダーの存在チェック
        if stripe_signature is None:
            logger.warning("Missing Stripe-Signature header")
            return Response(
                content=json.dumps({"error": "Missing Stripe-Signature header"}),
                status_code=400,
                media_type="application/json"
            )

        # Webhookシークレットキーが設定されていない場合
        if not WEBHOOK_SECRET:
            logger.error("Stripe webhook secret is not configured.")
            return Response(
                content=json.dumps({"error": "Webhook secret not configured"}),
                status_code=500,
                media_type="application/json"
            )

        # イベントの検証と構築
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, WEBHOOK_SECRET
        )
        logger.info(f"Webhook event verified: {event['id']}, type: {event['type']}")

        # イベントタイプに応じた処理
        event_type = event['type']
        event_data = event['data']['object']

        if event_type == 'payment_intent.succeeded':
            # 支払い成功時の処理
            payment_intent_id = event_data['id']
            amount = event_data['amount']
            currency = event_data['currency']
            customer_id = event_data.get('customer')
            metadata = event_data.get('metadata', {})

            logger.info(f"Payment succeeded: {payment_intent_id} for {amount} {currency}")

            # ここにデータベース更新などの処理を追加する
            # 例: 注文ステータスを更新、メール送信など
            # TODO: 実際の処理を実装

        elif event_type == 'payment_intent.payment_failed':
            # 支払い失敗時の処理
            payment_intent_id = event_data['id']
            error_message = event_data.get('last_payment_error', {}).get('message', 'Unknown error')

            logger.warning(f"Payment failed: {payment_intent_id} - {error_message}")

            # ここに支払い失敗時の処理を追加する
            # 例: 注文ステータスを更新、ユーザー通知など
            # TODO: 実際の処理を実装

        elif event_type == 'checkout.session.completed':
            # Checkoutセッション完了時の処理
            session_id = event_data['id']
            logger.info(f"Checkout session completed: {session_id}")

            # --- Stripe metadata から user_id, amount（ポイント数）を取得 ---
            metadata = event_data.get('metadata', {})
            user_id = metadata.get('user_id')
            amount = metadata.get('amount')
            if user_id is None or amount is None:
                logger.error(f"ポイント付与失敗: user_idまたはamountがmetadataにありません (metadata={metadata})")
            else:
                from app.features.points.services.apply_point_rule_service import apply_point_rule
                result = apply_point_rule(db, user_id, 'purchase', {'amount': amount})
                if result.get('success'):
                    logger.info(f"ポイント付与成功: user_id={user_id}, amount={amount}")
                else:
                    logger.error(f"ポイント付与エラー: {result.get('message')}")
        else:
            # その他のイベントタイプの処理
            logger.info(f"Unhandled event type: {event_type}")

        # 成功レスポンスを返す
        logger.info(f"Successfully processed event: {event['id']}")
        return Response(
            content=json.dumps({"status": "success", "event_id": event['id']}),
            status_code=200,
            media_type="application/json"
        )

    except ValueError as e:
        # 不正なペイロード
        logger.error(f"Invalid payload: {e}")
        return Response(
            content=json.dumps({"error": f"Invalid payload: {str(e)}"}),
            status_code=400,
            media_type="application/json"
        )

    except stripe.error.SignatureVerificationError as e:
        # 不正な署名
        logger.error(f"Invalid signature: {e}")
        return Response(
            content=json.dumps({"error": f"Invalid signature: {str(e)}"}),
            status_code=400,
            media_type="application/json"
        )

    except Exception as e:
        # その他の予期せぬエラー
        logger.exception(f"Unexpected error processing webhook: {e}")
        return Response(
            content=json.dumps({"error": "Internal server error"}),
            status_code=500,
            media_type="application/json"
        )
