from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import quote
from app.db.session import get_db
from app.features.account.repositories.account_repository import AccountRepository
from app.features.account.services.account_service import AccountService
from app.core.security import create_access_token, create_refresh_token  # `create_refresh_token` 
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
import logging
from app.features.points.services.points_service import process_point_event # points_serviceをインポート

router = APIRouter()

# デバッグ用ロガーの設定
logger = logging.getLogger(__name__)

# 1. LINE
@router.get("/login")
async def line_login(tr: str = None, tracking_id: str = None):
    # trパラメータを優先し、なければtracking_idを使用
    actual_tracking_id = tr or tracking_id
    logger.info(f"📥 LINE認証リクエスト受信 - tr={tr}, tracking_id={tracking_id}, actual={actual_tracking_id}")
    
    state = f"tracking_id={actual_tracking_id}" if actual_tracking_id else ""
    login_url = (
        f"https://access.line.me/oauth2/v2.1/authorize"
        f"?response_type=code"
        f"&client_id={LINE_LOGIN_CHANNEL_ID}"
        f"&redirect_uri={quote(REDIRECT_URI)}"
        f"&state={quote(state)}"
        f"&scope=profile%20openid"
    )
    
    logger.info(f"🔗 生成されたLINE認証URL: {login_url}")
    logger.info(f"🔗 stateパラメータ: '{state}'")
    
    return {"auth_url": login_url}


# 2. LINE
@router.get("/callback")
async def line_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing")
    
    # LINE API
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

    # LINE API
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_response = requests.get("https://api.line.me/v2/profile", headers=headers)
    if profile_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to retrieve user profile")

    profile = profile_response.json()
    line_id = profile.get("userId")
    display_name = profile.get("displayName")
    picture_url = profile.get("pictureUrl")

    # `tracking_id` 
    tracking_id = None
    if state:
        state_params = dict(param.split('=') for param in state.split('&') if '=' in param)
        tracking_id = state_params.get('tracking_id')

    # AccountService
    account_service = AccountService(db)
    logger.info(f"LINE認証: line_id={line_id}, display_name={display_name}")
    
    user = account_service.get_user_by_line_id(line_id)
    
    # JST
    jst = pytz.timezone('Asia/Tokyo')
    now_jst = datetime.now(jst).strftime("%Y/%m/%d %H:%M:%S")
    
    if not user:
        logger.info(f"新規ユーザー作成: line_id={line_id}")
        # AccountService
        user = account_service.create_user(
            line_id=line_id,
            nick_name=display_name,
            picture_url=picture_url,
            tracking_id=tracking_id,
            last_login=now_jst
        )
        logger.info(f"ユーザー作成完了: id={user.id}, invitation_id={user.invitation_id}")

        # 新規ユーザーがtracking_id経由で登録された場合、ポイントイベントを処理
        if tracking_id:
            process_point_event(
                db,
                'user_registered_by_referral',
                {'referred_user_id': user.id, 'tracking_id': tracking_id}
            )

    else:
        logger.info(f"既存ユーザー更新: id={user.id}, invitation_id={user.invitation_id}")
        # invitation_idが未設定の場合は設定する
        if not user.invitation_id:
            logger.info(f"invitation_idが未設定のため設定します: user_id={user.id}")
            user = account_service.ensure_user_has_invitation_id(user.id)
            logger.info(f"invitation_id設定完了: id={user.id}, invitation_id={user.invitation_id}")
        
        # 最終ログイン日時を更新
        user = account_service.update_last_login(line_id)

    # JWT
    jwt_token = create_access_token(
        user_id=user.id,
        user_type=user.user_type,
        affi_type=user.affi_type
    )

    # refresh_token 
    refresh_token = create_refresh_token(user.id)

    # `refresh_token` `HttpOnly Cookie` 
    #response = RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?token={jwt_token}")
    response = RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?token={jwt_token}&refresh_token={refresh_token}")
    
    #response.set_cookie(
    #    key="refresh_token",
    #    value=refresh_token,
    #    httponly=True,  # JavaScript 
    #    secure=True,  # http 
    #    samesite="None",  # 
    #    max_age=90 * 24 * 60 * 60,
    #    path="/"  # 
    #)

    logger.info(f"認証完了: user_id={user.id}, invitation_id={user.invitation_id}")
    return response
