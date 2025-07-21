# app/features/miniapp/services/miniapp_service.py

import requests
import os
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.features.account.services.account_service import AccountService
from app.features.miniapp.schemas.miniapp_schema import (
    LiffUserInfo, 
    UserRegistrationResponse,
    ErrorResponse
)
from app.db.models.user import User
# settings = get_settings()  # 一時的にコメントアウト

class MiniAppService:
    def __init__(self, db: Session):
        self.db = db
        self.account_service = AccountService(db)
        self.liff_id = '2007769669'  # LIFF用チャンネルID（ハードコード）
    
    async def verify_liff_id_token(self, id_token: str) -> Optional[LiffUserInfo]:
        """
        LIFF IDトークンをLINE APIで検証し、ユーザー情報を取得
        
        Args:
            id_token: LIFF IDトークン
            
        Returns:
            LiffUserInfo: 検証成功時のユーザー情報
            None: 検証失敗時
        """
        # 開発モード判定（複数条件でより確実に）
        is_dev_mode = (
            id_token.startswith('mock_') or 
            len(id_token) < 50 or  # 通常のLIFF IDトークンは長い
            id_token == 'mock_token_for_development' or
            'development' in id_token.lower()
        )
        
        if is_dev_mode:
            print(f"🔧 開発モード検出: IDトークン='{id_token[:20]}...' - LIFF検証をスキップ")
            import uuid
            dev_line_id = f"dev_user_{uuid.uuid4().hex[:12]}"
            print(f"🆔 開発用LINE ID生成: {dev_line_id}")
            return LiffUserInfo(
                line_id=dev_line_id,
                display_name="開発用ユーザー",
                picture_url=None
            )
        
        try:
            # LINE IDトークン検証API
            verify_url = "https://api.line.me/oauth2/v2.1/verify"
            
            data = {
                "id_token": id_token,
                "client_id": self.liff_id
            }
            
            response = requests.post(verify_url, data=data, timeout=10)
            
            if response.status_code != 200:
                print(f"LIFF ID token verification failed: {response.status_code}")
                return None
            
            token_info = response.json()
            
            # トークンの有効性を確認
            if token_info.get("client_id") != self.liff_id:
                print("Invalid client_id in token")
                return None
            
            # ユーザー情報を構築
            user_info = LiffUserInfo(
                line_id=token_info.get("sub"),
                display_name=token_info.get("name", ""),
                picture_url=token_info.get("picture")
            )
            
            return user_info
            
        except requests.exceptions.RequestException as e:
            print(f"Request error during LIFF token verification: {e}")
            return None
        except Exception as e:
            print(f"Error during LIFF token verification: {e}")
            return None
    
    async def register_or_update_user(
        self, 
        id_token: str, 
        user_type: str, 
        tracking_id: Optional[str] = None
    ) -> UserRegistrationResponse:
        """
        ユーザーを登録または更新
        
        Args:
            id_token: LIFF IDトークン
            user_type: ユーザータイプ (cast/customer)
            tracking_id: 招待コード
            
        Returns:
            UserRegistrationResponse: 登録結果
        """
        try:
            # LIFF IDトークンを検証
            user_info = await self.verify_liff_id_token(id_token)
            if not user_info:
                return UserRegistrationResponse(
                    success=False,
                    message="IDトークンの検証に失敗しました",
                    is_new_user=False
                )
            
            # 既存ユーザーを確認
            existing_user = self.account_service.get_user_by_line_id(user_info.line_id)
            
            if existing_user:
                # 既存ユーザーの場合、user_typeを更新（tracking_idは保持）
                return self._update_existing_user(existing_user, user_type, tracking_id)
            else:
                # 新規ユーザーの場合、作成
                return self._create_new_user(user_info, user_type, tracking_id)
                
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Database error during user registration: {e}")
            return UserRegistrationResponse(
                success=False,
                message="データベースエラーが発生しました",
                is_new_user=False
            )
        except Exception as e:
            print(f"Error during user registration: {e}")
            return UserRegistrationResponse(
                success=False,
                message="予期しないエラーが発生しました",
                is_new_user=False
            )
    
    def _update_existing_user(self, user: User, user_type: str, tracking_id: Optional[str]) -> UserRegistrationResponse:
        """既存ユーザーのuser_typeを更新（tracking_idは既存値を保持）"""
        try:
            # user_typeは常に更新
            user.user_type = user_type
            
            # tracking_idは既存値がない場合のみ更新
            if not user.tracking_id and tracking_id:
                user.tracking_id = tracking_id
            
            self.db.commit()
            self.db.refresh(user)
            
            # tracking_idの更新状況をメッセージに反映
            message = "ユーザー情報を更新しました"
            if user.tracking_id and tracking_id and user.tracking_id != tracking_id:
                message += "（紹介コードは既に登録済みのため変更されませんでした）"
            
            return UserRegistrationResponse(
                success=True,
                message=message,
                user_id=user.id,
                user_type=user.user_type,
                is_new_user=False
            )
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def _create_new_user(
        self, 
        user_info: LiffUserInfo, 
        user_type: str, 
        tracking_id: Optional[str]
    ) -> UserRegistrationResponse:
        """新規ユーザーを作成"""
        try:
            # ユーザーデータを準備
            user_data = {
                "line_id": user_info.line_id,
                "nick_name": user_info.display_name,
                "picture_url": user_info.picture_url,
                "user_type": user_type,
                "tracking_id": tracking_id
            }
            
            # AccountServiceを使用してユーザーを作成
            new_user = self.account_service.create_user(**user_data)
            
            return UserRegistrationResponse(
                success=True,
                message="新しいユーザーを作成しました",
                user_id=new_user.id,
                user_type=new_user.user_type,
                is_new_user=True
            )
            
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_user_by_line_id(self, line_id: str) -> Optional[User]:
        """LINE IDでユーザーを取得"""
        return self.account_service.get_user_by_line_id(line_id)