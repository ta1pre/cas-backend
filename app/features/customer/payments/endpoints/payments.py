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
from app.db.models.stripe_event import StripeEvent
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
    logger.info("[Webhook] Webhook received") # INFOレベルで受信ログ

    try:
        # リクエストボディを読み取る
        payload = await request.body()
        logger.info(f"[Webhook] Received payload (first 100 bytes): {payload[:100]}...")

        # Stripe-Signatureヘッダーの存在チェック
        if stripe_signature is None:
            logger.warning("[Webhook] Missing Stripe-Signature header")
            return Response(
                content=json.dumps({"error": "Missing Stripe-Signature header"}),
                status_code=400,
                media_type="application/json"
            )

        # Webhookシークレットキーが設定されていない場合
        if not WEBHOOK_SECRET:
            logger.error("[Webhook] Stripe webhook secret is not configured.")
            return Response(
                content=json.dumps({"error": "Webhook secret not configured"}),
                status_code=500,
                media_type="application/json"
            )

        # イベントの検証と構築
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, WEBHOOK_SECRET
        )
        logger.info(f"[Webhook] Webhook event verified: {event['id']}, type: {event['type']}")

        event_type = event["type"]
        # イベントタイプに応じた処理
        if event_type == "payment_intent.succeeded":
            obj = event["data"]["object"]
            user_id = obj.get("metadata", {}).get("user_id")
            point_value = obj.get("metadata", {}).get("point_value")
            if not user_id or not point_value:
                logger.error(f"[Webhook] 必須情報なし: user_id={user_id}, point_value={point_value}")
                return Response(
                    content=json.dumps({"error": "user_id or point_value missing"}),
                    status_code=400,
                    media_type="application/json"
                )
            logger.info(f"[Webhook] payment_intent.succeeded: user_id={user_id}, point_value={point_value}")
            event_id = event.get("id")
            if not event_id:
                logger.error("[Webhook] Stripe eventにIDがありません")
                return Response(
                    content=json.dumps({"error": "Stripe eventにIDがありません"}),
                    status_code=400,
                    media_type="application/json"
                )
            # 既に処理済みかチェック
            exists = db.query(StripeEvent).filter(StripeEvent.event_id == event_id).first()
            if exists:
                logger.warning(f"[Webhook] StripeイベントID {event_id} は既に処理済み（二重実行防止）")
                return Response(
                    content=json.dumps({"error": "このイベントは既に処理済みです"}),
                    status_code=200,  # Stripeには200を返すことで再送を防ぐ
                    media_type="application/json"
                )
            # ここでStripeEventを先に記録（ロールバック時は消える）
            new_event = StripeEvent(event_id=event_id)
            db.add(new_event)
            db.flush()  # ID付与のため
            from app.features.points.services.apply_point_rule_service import apply_point_rule
            try:
                apply_point_rule(
                    db=db,
                    user_id=int(user_id),
                    rule_name="purchase",
                    variables={"amount": int(point_value)},
                    transaction_type="buyin",
                )
                # StripeEventにuser_id, transaction_idを記録（commit前なのでID取得可）
                new_event.user_id = int(user_id)
                # transaction_idはapply_point_ruleの返り値から取得可能ならセット
            except Exception as e:
                logger.error(f"[Webhook] ポイント付与処理でエラー: {e}")
                return Response(
                    content=json.dumps({"error": "apply_point_rule error"}),
                    status_code=500,
                    media_type="application/json"
                )
        elif event_type == 'payment_intent.payment_failed':
            payment_intent_id = event["data"]["object"]["id"]
            logger.warning(f"[Webhook] Payment failed: {payment_intent_id}")
        else:
            logger.info(f"[Webhook] Unhandled event type: {event_type}")

        db.commit()
        # 成功レスポンスを返す
        logger.info(f"[Webhook] Successfully processed event: {event['id']}")
        return Response(
            content=json.dumps({"status": "success", "event_id": event['id']}),
            status_code=200,
            media_type="application/json"
        )

    except ValueError as e:
        # 不正なペイロード
        logger.error(f"[Webhook] Invalid payload: {e}")
        return Response(
            content=json.dumps({"error": f"Invalid payload: {str(e)}"}),
            status_code=400,
            media_type="application/json"
        )

    except stripe.error.SignatureVerificationError as e:
        # 不正な署名
        logger.error(f"[Webhook] Invalid signature: {e}")
        return Response(
            content=json.dumps({"error": f"Invalid signature: {str(e)}"}),
            status_code=400,
            media_type="application/json"
        )

    except Exception as e:
        # その他の予期せぬエラー
        logger.exception(f"[Webhook] Unexpected error processing webhook: {e}")
        return Response(
            content=json.dumps({"error": "Internal server error"}),
            status_code=500,
            media_type="application/json"
        )
