from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import quote
from app.db.session import get_db
from app.features.account.repositories.account_repository import AccountRepository
from app.core.security import create_access_token, create_refresh_token  # ✅ `create_refresh_token` を追加
from app.core.config import (
    FRONTEND_URL, 
    LINE_LOGIN_CHANNEL_ID, 
    LINE_LOGIN_CHANNEL_SECRET, 
    REDIRECT_URI,
    REFRESH_TOKEN_EXPIRE_DAYS
)
import requests
from datetime import datetime
import pytz

router = APIRouter()

# ✅ 1. LINEログインURL生成
@router.get("/login")
async def line_login(tracking_id: str = None):
    state = f"tracking_id={tracking_id}" if tracking_id else ""
    login_url = (
        f"https://access.line.me/oauth2/v2.1/authorize"
        f"?response_type=code"
        f"&client_id={LINE_LOGIN_CHANNEL_ID}"
        f"&redirect_uri={quote(REDIRECT_URI)}"
        f"&state={quote(state)}"
        f"&scope=profile%20openid"
    )
    return {"auth_url": login_url}


# ✅ 2. LINEコールバック処理
@router.get("/callback")
async def line_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing")
    
    # 🔑 LINE APIからトークン取得
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": LINE_LOGIN_CHANNEL_ID,
        "client_secret": LINE_LOGIN_CHANNEL_SECRET
    }
    response = requests.post("https://api.line.me/oauth2/v2.1/token", data=token_data)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to retrieve access token")

    access_token = response.json().get("access_token")

    # 🔑 LINE APIからユーザープロフィール取得
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_response = requests.get("https://api.line.me/v2/profile", headers=headers)
    if profile_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to retrieve user profile")

    profile = profile_response.json()
    line_id = profile.get("userId")
    display_name = profile.get("displayName")
    picture_url = profile.get("pictureUrl")

    # 🔗 `tracking_id` を state から抽出
    tracking_id = None
    if state:
        state_params = dict(param.split('=') for param in state.split('&') if '=' in param)
        tracking_id = state_params.get('tracking_id')

    # 🔑 ユーザー確認・登録
    account_repo = AccountRepository(db)
    user = account_repo.get_user_by_line_id(line_id)
    
    # ✅ JSTの現在時刻を取得
    jst = pytz.timezone('Asia/Tokyo')
    now_jst = datetime.now(jst).strftime("%Y/%m/%d %H:%M:%S")
    
    if not user:
        # 新規ユーザー登録
        user = account_repo.create_user(
            line_id=line_id,
            nick_name=display_name,
            picture_url=picture_url,
            tracking_id=tracking_id,
            last_login=now_jst
        )
    else:
        # 再ログイン → last_login更新
        user = account_repo.update_last_login(line_id)

    # 📌 JWTトークン生成
    jwt_token = create_access_token(
        user_id=user.id,
        user_type=user.user_type,
        affi_type=user.affi_type
    )

    # 🚀 refresh_token を生成
    refresh_token = create_refresh_token(user.id)

    # ✅ `refresh_token` を `HttpOnly Cookie` に保存
    #もともとはこっちresponse = RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?token={jwt_token}")
    response = RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?token={jwt_token}&refresh_token={refresh_token}")
    
    #response.set_cookie(
    #    key="refresh_token",
    #    value=refresh_token,
    #    httponly=True,  # JavaScript からアクセスできない
    #    secure=True,  # 開発環境で http を使う場合は False に設定
    #    samesite="None",  # クロスサイトリクエスト制限
    #    max_age=90 * 24 * 60 * 60,
    #    path="/"  # 全てのパスで有効にする
    #)


    return response
