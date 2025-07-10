# app/api/v1/routers/master_router.py

from fastapi import APIRouter

# マスタールーターのインスタンス生成
master_router = APIRouter()

# ヘルスチェック用エンドポイント
@master_router.get("/health")
def health_check():
    return {"status": "ok"}

# LINEBOT関連ルーター
from app.features.linebot.endpoints.linebot_routers import linebot_router
master_router.include_router(linebot_router, prefix="/linebot", tags=["Linebot"])

# ACCOUNT関連ルーター
from app.features.account.endpoints.account_routers import account_router
master_router.include_router(account_router, prefix="/account", tags=["Account"])

# SETUP関連ルーター 
from app.features.setup.endpoints.setup_routers import setup_router
master_router.include_router(setup_router, prefix="/setup", tags=["Setup"])

# SMS関連ルーター
from app.features.sms.endpoints.sms_routers import sms_router
master_router.include_router(sms_router, prefix="/sms", tags=["SMS"])

# MEDIA関連ルーター
from app.features.media.endpoints.media_routers import media_router
master_router.include_router(media_router, prefix="/media", tags=["Media"])

# traits関連ルーター
from app.features.cast.traits.endpoints.traits_routers import traits_router
master_router.include_router(traits_router, prefix="/traits", tags=["Traits"])

# servicetype関連ルーター
from app.features.cast.servicetype.endpoints.servicetype_routers import servicetype_router
master_router.include_router(servicetype_router, prefix="/servicetype", tags=["ServiceType"])

# 本人確認関連ルーター
from app.features.cast.identity_verification.endpoints.identity_routers import identity_router
master_router.include_router(identity_router, prefix="/cast/identity-verification", tags=["Identity Verification"])

# ADMIN関連ルーター
from app.features.admin.test_login.endpoints.test_login_routers import test_login_router
master_router.include_router(test_login_router, prefix="/admin/test-login", tags=["Admin"])

# === Admin - Cast 管理ルーター ===
from app.features.admin.cast.endpoints.cast_routers import admin_cast_router
master_router.include_router(admin_cast_router, prefix="/admin/cast", tags=["Admin - Cast"])

# Tenant（管理アカウント管理）
from app.features.admin.tenant.endpoints.tenant_routers import tenant_router
master_router.include_router(
    tenant_router,
    prefix="/admin/tenant",
    tags=["Tenant"]
)

# WITHDRAWAL - 出金申請
from app.features.withdrawal.endpoints.withdrawal_router import withdrawal_router
master_router.include_router(withdrawal_router, prefix="/withdrawal", tags=["Withdrawal"])

# POINT - ポイント
from app.features.points.endpoints.points_routers import media_router as points_router
master_router.include_router(points_router, prefix="/points", tags=["Points"])

# CUSTOMER - 検索API
from app.features.customer.search.endpoints.search_routers import search_router
master_router.include_router(search_router, prefix="/customer/search", tags=["Customer - Search"])

# CUSTOMER - キャストプロフィール
from app.features.customer.castprof.endpoints.castprof_routers import castprof_router
master_router.include_router(castprof_router, prefix="/customer/castprof", tags=["Customer - CastProf"])

# CUSTOMER - エリア設定
from app.features.customer.area.endpoints.area_routers import area_router
master_router.include_router(area_router, prefix="/customer/area", tags=["Customer - Area"])

# CUSTOMER - お気に入り
from app.features.customer.favorites.endpoints.favorites_routers import favorites_router
from app.features.customer.payments.endpoints.payments_routers import customer_payments_router, webhook_router

# Customer向け機能
master_router.include_router(favorites_router, prefix="/customer/favorites")
master_router.include_router(customer_payments_router) # prefixはpayments_routers.pyで定義済み

# Webhook (認証不要なルートはこちらに追加する想定)
master_router.include_router(webhook_router) # prefixはpayments_routers.pyで定義済み

# CUSTOMER - 検索API
from app.features.customer.search.endpoints.search_routers import search_router
master_router.include_router(search_router, prefix="/customer/search", tags=["Customer - Search"])

# CUSTOMER - キャストプロフィール
from app.features.customer.castprof.endpoints.castprof_routers import castprof_router
master_router.include_router(castprof_router, prefix="/customer/castprof", tags=["Customer - CastProf"])

# CUSTOMER - エリア設定
from app.features.customer.area.endpoints.area_routers import area_router
master_router.include_router(area_router, prefix="/customer/area", tags=["Customer - Area"])

# RESERVE - 予約
from app.features.reserve.endpoints.reserve_routers import reserve_router
master_router.include_router(reserve_router, prefix="/reserve", tags=["Reserve"])

# 駅の距離を計算！ディレクトリ「_駅の距離」　INSERT DISTANCE ルーター（新規）
# from app.features.insertDistances.insert_distance_router import insert_distance_router
# master_router.include_router(insert_distance_router, prefix="/insert-distance", tags=["Insert Distance"])

# Cast Profile (New)
from app.features.cast.prof.endpoints.prof_routers import prof_router
master_router.include_router(
    prof_router,  
    prefix="/cast/prof",
    tags=["Cast Profile"]
)

# Cast Available（キャスト利用可能API）
from app.features.cast.available.endpoints.available_routers import available_router
master_router.include_router(available_router, prefix="/cast", tags=["Cast - Available"])

# User Profile（ユーザープロフィール情報）
from app.features.customer.user_profile.endpoints.user_profile_routers import user_profile_router
master_router.include_router(
    user_profile_router,
    prefix="/user",
    tags=["User Profile"]
)

# POSTS - ミニブログ機能
from app.features.posts.endpoints.post_routers import posts_router
master_router.include_router(posts_router, prefix="/posts", tags=["Posts"])

# テナント用APIルーターを /tenants でincludeする
from app.features.tenant.endpoints.tenant_routers import tenant_router
master_router.include_router(
    tenant_router,
    prefix="/tenants",
    tags=["Tenants"]
)

# REFERRAL - 紹介機能
from app.features.referral.endpoints.referral_routers import referral_router
master_router.include_router(referral_router, prefix="/referral", tags=["Referral"])
