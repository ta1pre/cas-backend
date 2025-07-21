# app/features/miniapp/endpoints/miniapp_routers.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.features.miniapp.services.miniapp_service import MiniAppService
from app.features.miniapp.schemas.miniapp_schema import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    UserUpdateRequest,
    ErrorResponse
)
from app.db.session import get_db

# ルーターの作成
miniapp_router = APIRouter()

@miniapp_router.post(
    "/register",
    response_model=UserRegistrationResponse,
    summary="ユーザー登録",
    description="LINEミニアプリからのユーザー登録・更新",
    tags=["MiniApp"]
)
async def register_user(
    request: UserRegistrationRequest,
    db: Session = Depends(get_db)
) -> UserRegistrationResponse:
    """
    LINEミニアプリからのユーザー登録・更新
    
    - LIFF IDトークンを検証
    - 新規ユーザーの場合：ユーザーを作成
    - 既存ユーザーの場合：user_typeを更新
    
    Args:
        request: ユーザー登録リクエスト
        db: データベースセッション
        
    Returns:
        UserRegistrationResponse: 登録結果
        
    Raises:
        HTTPException: リクエストが無効な場合
    """
    try:
        # サービスの初期化
        miniapp_service = MiniAppService(db)
        
        # ユーザー登録・更新処理
        result = await miniapp_service.register_or_update_user(
            id_token=request.id_token,
            user_type=request.user_type,
            tracking_id=request.tracking_id
        )
        
        # 失敗時はHTTPExceptionを発生
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
        
        return result
        
    except HTTPException:
        # HTTPExceptionは再発生
        raise
    except Exception as e:
        # その他の例外はサーバーエラーとして処理
        print(f"Unexpected error in register_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="サーバーエラーが発生しました"
        )

@miniapp_router.post(
    "/verify-token",
    summary="IDトークン検証",
    description="LIFF IDトークンの検証のみ実行",
    tags=["MiniApp"]
)
async def verify_id_token(
    id_token: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    LIFF IDトークンの検証のみ実行
    
    Args:
        id_token: LIFF IDトークン
        db: データベースセッション
        
    Returns:
        Dict: 検証結果とユーザー情報
        
    Raises:
        HTTPException: IDトークンが無効な場合
    """
    try:
        # サービスの初期化
        miniapp_service = MiniAppService(db)
        
        # IDトークン検証
        user_info = await miniapp_service.verify_liff_id_token(id_token)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="IDトークンの検証に失敗しました"
            )
        
        # 既存ユーザーの確認
        existing_user = miniapp_service.get_user_by_line_id(user_info.line_id)
        
        return {
            "success": True,
            "user_info": user_info.dict(),
            "is_existing_user": existing_user is not None,
            "user_type": existing_user.user_type if existing_user else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in verify_id_token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="サーバーエラーが発生しました"
        )

@miniapp_router.get(
    "/health",
    summary="ヘルスチェック",
    description="ミニアプリAPIのヘルスチェック",
    tags=["MiniApp"]
)
def health_check() -> Dict[str, str]:
    """
    ミニアプリAPIのヘルスチェック
    
    Returns:
        Dict: ステータス情報
    """
    return {
        "status": "ok",
        "service": "miniapp"
    }