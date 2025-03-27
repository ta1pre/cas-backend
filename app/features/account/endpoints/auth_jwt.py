from fastapi import APIRouter, Depends, HTTPException, Security, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone 
from app.core.security import create_access_token, create_refresh_token, verify_access_token, verify_refresh_token
from app.db.session import get_db
from app.features.account.repositories.account_repository import AccountRepository
from app.core.config import (
    REFRESH_TOKEN_EXPIRE_DAYS
)
import logging
import json


logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# ✅ 環境変数から `Secure` の設定を動的に変更
import os
IS_PRODUCTION = os.getenv("ENV") == "production"

# ✅ リクエストモデル定義
class TokenRequest(BaseModel):
    user_id: int

# 📌 JWTトークン生成（ログイン時）
@router.post("/token")
def generate_jwt_token(response: Response, request: TokenRequest, db: Session = Depends(get_db)):

    user_repo = AccountRepository(db)
    user = user_repo.get_user_by_id(request.user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token(user.id, user.user_type, user.affi_type)
    refresh_token = create_refresh_token(user.id)

    # ✅ `refresh_token` を `HttpOnly Cookie` に保存
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # ✅ 本番環境なら `Secure=True`
        samesite="None",
        max_age=90 * 24 * 60 * 60,
    )

    return {"access_token": access_token, "token_type": "bearer"}

# ✅ `access_token` を検証（通常のAPIリクエストで呼ばれる）
@router.get("/verify")
def verify_jwt_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    """
    `access_token` の有効性を検証する
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="No valid token provided")

    token = credentials.credentials
    try:
        token_data = verify_access_token(token)
        user_id = token_data.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload: user_id is missing")

        user_repo = AccountRepository(db)
        user = user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # ✅ `Set-Cookie` を明示的に設定（CORSエラー回避）
        response = Response()
        response.set_cookie(
            key="test_cookie",
            value="test_value",
            httponly=True,
            secure=True,
            samesite="None"
        )

        return {
            "user_id": user.id,
            "user_type": user.user_type,
            "affi_type": user.affi_type,
            "message": "Token is valid"
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token Error: {str(e)}")

# トークンを新しくする
@router.post("/refresh")
async def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    logger.info("🚀 [refresh] トークン更新リクエスト受信")

    # ✅ `Authorization` ヘッダーから `refresh_token` を取得
    auth_header = request.headers.get("Authorization")
    refresh_token = None

    if auth_header and auth_header.startswith("Bearer "):
        refresh_token = auth_header.split("Bearer ")[1]

    logger.info(f"🔍 受信した refresh_token: {refresh_token}")

    if not refresh_token:
        logger.warning("⛔ 有効なリフレッシュトークンが提供されていません")
        raise HTTPException(status_code=401, detail="No valid refresh token provided")

    try:
        # ✅ `refresh_token` の検証
        token_data = verify_refresh_token(refresh_token)

        # user_id を取得
        user_id = token_data.get("user_id")
        if not user_id:
            logger.warning("⛔ `refresh_token` のペイロードに `user_id` が含まれていません")
            raise HTTPException(status_code=401, detail="Invalid refresh token payload")

        # ✅ `AccountRepository` を使って `user_type` を取得
        account_repo = AccountRepository(db)
        user = account_repo.get_user_by_id(user_id)

        if not user:
            logger.warning(f"⛔ ユーザーがデータベースに存在しません: user_id={user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"🔹 DBから取得した `user_type`: {user.user_type}, `affi_type`: {user.affi_type}")

        # ✅ `create_access_token` に `user_type` と `affi_type` を渡す
        new_token = create_access_token(user_id, user.user_type, user.affi_type)
        logger.info(f"✅ 新しい認証トークンを発行: {new_token}")

        return {"token": new_token}

    except Exception as e:
        logger.error(f"⛔ リフレッシュトークンの検証エラー: {str(e)}")
        raise HTTPException(status_code=401, detail="Refresh Token Error")


#refresh_token の有効期限を検証
@router.post("/extend_refresh_token")
async def extend_refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    `refresh_token` の有効期限を確認し、24時間未満なら新しい `refresh_token` を発行
    """
    print(f"🚀 【extend_refresh_token】 リクエストを今から受信")

    # ✅ 受信したリクエストボディをログに出力
    try:
        body = await request.json()
        refresh_token = body.get("refresh_token")
    except json.JSONDecodeError:
        print("⛔ 【extend_refresh_token】 リクエストボディのパースに失敗")
        raise HTTPException(status_code=400, detail="Invalid request format")

    print(f"🚀 【extend_refresh_token】 リクエスト受信 - refresh_token: {refresh_token}")

    if not refresh_token:
        print("⛔ 【extend_refresh_token】 `refresh_token` がリクエストボディに含まれていません")
        raise HTTPException(status_code=401, detail="No valid refresh token provided")

    try:
        # ✅ `refresh_token` の検証
        token_data = verify_refresh_token(refresh_token)
        exp_timestamp = token_data.get("exp")
        user_id = token_data.get("user_id")

        if not user_id or not exp_timestamp:
            print("⛔ 【extend_refresh_token】 `refresh_token` のペイロードが無効: user_id または exp がありません")
            raise HTTPException(status_code=401, detail="Invalid refresh token payload")

        # ✅ 現在の UNIX 時間（秒）
        current_timestamp = int(datetime.now(timezone.utc).timestamp())
        remaining_time = exp_timestamp - current_timestamp  # 有効期限までの残り時間（秒）

        print(f"🕒 【extend_refresh_token】 現在時刻: {current_timestamp} / refresh_token 有効期限: {exp_timestamp} / 残り {remaining_time} 秒")

        # 🔹 期限が 60日未満なら、新しい refresh_token を発行
        if remaining_time < 90 * 24 * 60 * 60:  # 60日未満なら更新
            new_refresh_token = create_refresh_token(user_id)
            print(f"🔄 【extend_refresh_token】 `refresh_token` の期限が近いため更新: {new_refresh_token}")

            return {"refresh_token": new_refresh_token}

        print("✅ 【extend_refresh_token】 refresh_tokenはまだ有効 - 更新不要")
        return {"message": "refresh_token is still valid"}

    except Exception as e:
        print(f"⛔ 【extend_refresh_token】 エラー: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Refresh Token Error: {str(e)}")