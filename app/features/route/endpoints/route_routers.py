# app/features/route/endpoints/route_routers.py

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import quote
from app.db.session import get_db
from app.features.account.services.account_service import AccountService
from app.core.config import FRONTEND_URL
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# ページマッピング定義
PAGE_MAPPINGS = {
    "cast": {
        "home": "/p/cast/dashboard",
        "reserve": "/p/cast/reserve", 
        "sales": "/p/cast/earnings",
        "profile": "/p/cast/profile",
        "message": "/p/cast/cont/posts",
        "settings": "/p/cast/settings"
    },
    "customer": {
        "home": "/p/customer/dashboard",
        "search": "/p/customer/search",
        "favorite": "/p/customer/favorites", 
        "history": "/p/customer/history",
        "profile": "/p/customer/profile",
        "payment": "/p/customer/payments"
    },
    "default": {
        "login": "/auth/login",
        "help": "/help",
        "about": "/about", 
        "terms": "/terms"
    }
}

# 認証不要ページ
PUBLIC_PAGES = ["/help", "/about", "/terms", "/auth/login"]

@router.get("/{action}")
async def route_handler(
    action: str, 
    request: Request,
    type: str = "default",
    db: Session = Depends(get_db)
):
    """
    リッチメニューからのルーティング処理
    
    Args:
        action: アクション名 (home, reserve, help など)
        type: ユーザータイプ (cast, customer, default)
        request: FastAPIリクエスト
        db: データベースセッション
    """
    try:
        logger.info(f"Route request: action={action}, type={type}")
        
        # ページマッピングから目的地を取得
        destination = _get_destination(action, type)
        if not destination:
            raise HTTPException(status_code=404, detail=f"Page not found: {action}")
        
        logger.info(f"Destination: {destination}")
        
        # 認証不要ページの場合は直接リダイレクト
        if destination in PUBLIC_PAGES:
            logger.info(f"Public page redirect: {destination}")
            return RedirectResponse(url=f"{FRONTEND_URL}{destination}")
        
        # 認証が必要なページの場合、認証状況をチェック
        line_id = _extract_line_id_from_request(request)
        
        if line_id and _is_user_authenticated(line_id, db):
            # 認証済みの場合は直接目的ページへ
            logger.info(f"Authenticated user redirect: {destination}")
            return RedirectResponse(url=f"{FRONTEND_URL}{destination}")
        else:
            # 未認証の場合はログイン経由で目的ページへ
            logger.info(f"Unauthenticated user, login required for: {destination}")
            tracking_id = f"route_{action}_{type}"
            
            # destinationをエンコードしてLINE認証へ
            login_url = (
                f"/api/v1/account/line/login"
                f"?tr={tracking_id}"
                f"&destination={quote(destination)}"
            )
            return RedirectResponse(url=login_url)
            
    except Exception as e:
        logger.error(f"Route error: {str(e)}")
        # エラー時はデフォルトページへ
        return RedirectResponse(url=f"{FRONTEND_URL}/")

def _get_destination(action: str, user_type: str) -> str:
    """アクションとユーザータイプから目的地URLを取得"""
    mapping = PAGE_MAPPINGS.get(user_type, {})
    return mapping.get(action)

def _extract_line_id_from_request(request: Request) -> str:
    """リクエストからLINE IDを抽出（今回は簡易実装）"""
    # 実際の実装では、リクエストヘッダーやクッキーから認証情報を取得
    # LINE Browserの場合、特定のヘッダーが送信される可能性がある
    
    # LINEアプリからのアクセスかどうかをUser-Agentで判定
    user_agent = request.headers.get("user-agent", "")
    if "Line" in user_agent:
        # LINEアプリからのアクセスの場合、追加の処理が可能
        # ここでは簡易的にNoneを返す（認証チェックをスキップ）
        return None
    
    return None

def _is_user_authenticated(line_id: str, db: Session) -> bool:
    """ユーザーが認証済みかどうかをチェック"""
    if not line_id:
        return False
    
    try:
        account_service = AccountService(db)
        user = account_service.get_user_by_line_id(line_id)
        return user is not None
    except:
        return False