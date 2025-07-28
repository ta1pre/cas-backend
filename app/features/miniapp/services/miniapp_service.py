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
# MenuManagerはエラーの原因のため削除
# from app.features.linebot.rich_menu.services.menu_manager import MenuManager
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
            import uuid
            dev_line_id = f"dev_user_{uuid.uuid4().hex[:12]}"
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
                return None
            
            token_info = response.json()
            
            # トークンの有効性を確認（audフィールドをチェック）
            if token_info.get("aud") != self.liff_id:
                return None
            
            # ユーザー情報を構築
            user_info = LiffUserInfo(
                line_id=token_info.get("sub"),
                display_name=token_info.get("name", ""),
                picture_url=token_info.get("picture")
            )
            
            return user_info
            
        except requests.exceptions.RequestException:
            return None
        except Exception:
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
                
        except SQLAlchemyError:
            self.db.rollback()
            return UserRegistrationResponse(
                success=False,
                message="データベースエラーが発生しました",
                is_new_user=False
            )
        except Exception:
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
            
            # setup_statusをcompletedに更新
            user.setup_status = 'completed'
            
            self.db.commit()
            self.db.refresh(user)
            
            # Rich Menuを更新
            self._update_user_rich_menu(user.line_id, user.user_type)
            
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
                "tracking_id": tracking_id,
                "setup_status": "completed"  # 初回登録時にcompletedに設定
            }
            
            # AccountServiceを使用してユーザーを作成
            new_user = self.account_service.create_user(**user_data)
            
            # Rich Menuを更新
            self._update_user_rich_menu(new_user.line_id, new_user.user_type)
            
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
    
    def _update_user_rich_menu(self, line_id: str, user_type: str):
        """
        ユーザーのRich Menuを更新（新しいメニューシステム対応）
        
        Args:
            line_id: LINE ID
            user_type: ユーザータイプ（cast, customer, など）
        """
        try:
            # 新しいメニューシステムを使用
            from app.features.linebot.rich_menu.menu_selector import MenuSelector
            
            # ユーザー情報を取得
            user = self.get_user_by_line_id(line_id)
            if not user:
                print(f"Rich Menu更新失敗: ユーザーが見つかりません - LINE ID: {line_id}")
                return
            
            # メニューセレクターを初期化
            selector = MenuSelector()
            
            # ユーザーコンテキストを構築
            user_context = {
                'user_type': user.user_type,
                'identity_status': self._get_identity_status(user)
            }
            
            # 適切なメニューを選択
            menu_type = selector.select_menu(user_context)
            print(f"選択されたメニュータイプ: {menu_type} (LINE ID: {line_id})")
            
            # メニューを設定
            self._set_menu_by_type(line_id, menu_type)
                
        except Exception as e:
            print(f"Rich Menu更新エラー: {line_id} -> {str(e)}")
    
    def _get_identity_status(self, user) -> Optional[str]:
        """
        ユーザーの身分証確認ステータスを取得
        
        Args:
            user: Userモデルのインスタンス
        
        Returns:
            Optional[str]: 身分証ステータス（approved, pending, rejected, unsubmitted, None）
        """
        try:
            # キャスト以外の場合はNoneを返す
            if user.user_type != 'cast':
                return None
            
            # cast_identity_verificationテーブルから情報を取得
            from app.db.models.cast_identity_verification import CastIdentityVerification
            
            verification = self.db.query(CastIdentityVerification).filter(
                CastIdentityVerification.cast_id == user.id
            ).first()
            
            if verification:
                return verification.status
            else:
                # レコードがない場合は未提出扱い
                return None
                
        except Exception as e:
            print(f"身分証ステータス取得エラー: {user.id} -> {str(e)}")
            return None
    
    def _set_menu_by_type(self, line_id: str, menu_type: str):
        """
        メニュータイプに基づいてリッチメニューを設定
        
        Args:
            line_id: LINE ID
            menu_type: メニュータイプ
        """
        try:
            # リッチメニュー一覧を取得
            menu_list = self._get_rich_menu_list()
            if not menu_list or not menu_list.get("richmenus"):
                print(f"Rich Menu設定失敗: 利用可能なメニューがありません")
                return
            
            # メニュータイプに対応するメニューIDを取得
            menu_id = self._find_menu_id_by_type(menu_type, menu_list)
            if not menu_id:
                print(f"Rich Menu設定失敗: {menu_type}に対応するメニューが見つかりません")
                return
            
            # リッチメニューを設定
            success = self._set_rich_menu(line_id, menu_id)
            if success:
                print(f"Rich Menu設定成功: {line_id} -> {menu_type} (menu_id: {menu_id})")
            else:
                print(f"Rich Menu設定失敗: {line_id} -> {menu_type} (menu_id: {menu_id})")
                
        except Exception as e:
            print(f"Rich Menu設定エラー: {line_id} -> {str(e)}")
    
    def _find_menu_id_by_type(self, menu_type: str, menu_list: dict) -> Optional[str]:
        """
        メニュータイプに対応するメニューIDを検索
        
        Args:
            menu_type: メニュータイプ
            menu_list: LINE APIから取得したメニューリスト
        
        Returns:
            Optional[str]: メニューID
        """
        richmenus = menu_list.get("richmenus", [])
        
        # 完全一致で検索
        for menu in richmenus:
            if menu.get("name") == menu_type:
                return menu["richMenuId"]
        
        # 見つからない場合はデフォルトメニューを検索
        for menu in richmenus:
            if menu.get("name") == "default":
                print(f"デフォルトメニューを使用: {menu_type} -> default")
                return menu["richMenuId"]
        
        return None

    def _get_rich_menu_list(self):
        """LINE公式アカウントに登録されているリッチメニューの一覧を取得"""
        try:
            url = "https://api.line.me/v2/bot/richmenu/list"
            headers = {
                "Authorization": f"Bearer {os.getenv('LINE_CHANNEL_ACCESS_TOKEN')}"
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"リッチメニュー一覧取得失敗: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"リッチメニュー一覧取得エラー: {str(e)}")
            return None

    def _get_menu_id_by_user_type(self, user_type: str, menu_list: dict) -> str:
        """ユーザータイプに基づいて適切なリッチメニューIDを取得"""
        richmenus = menu_list.get("richmenus", [])
        
        # user_typeに応じたメニュー名を定義
        menu_name_map = {
            "cast": "cast_menu",
            "customer": "customer_menu"
        }
        
        target_menu_name = menu_name_map.get(user_type, "default")
        
        # 指定されたメニュー名を探す
        for menu in richmenus:
            menu_name = menu.get("name", "").lower()
            if target_menu_name.lower() in menu_name:
                print(f"メニュー選択: {user_type} -> {target_menu_name} (ID: {menu['richMenuId']})")
                return menu["richMenuId"]
        
        # 指定メニューが見つからない場合はdefaultを探す
        for menu in richmenus:
            if "default" in menu.get("name", "").lower():
                print(f"デフォルトメニューを使用: {user_type} -> default (ID: {menu['richMenuId']})")
                return menu["richMenuId"]
        
        # defaultも見つからない場合は最初のメニューを使用
        if richmenus:
            print(f"最初のメニューを使用: {user_type} -> {richmenus[0].get('name', 'unknown')} (ID: {richmenus[0]['richMenuId']})")
            return richmenus[0]["richMenuId"]
        
        # メニューが見つからない場合は作成を試みる
        print(f"リッチメニューが見つからないため、作成を試みます: {user_type}")
        self._ensure_menus_exist()
        
        # 再度取得を試みる
        menu_list_retry = self._get_rich_menu_list()
        if menu_list_retry and menu_list_retry.get("richmenus"):
            return self._get_menu_id_by_user_type(user_type, menu_list_retry)
        
        return None

    def _set_rich_menu(self, line_id: str, menu_id: str) -> bool:
        """LINE Messaging APIを直接使用してリッチメニューを設定"""
        try:
            url = f"https://api.line.me/v2/bot/user/{line_id}/richmenu/{menu_id}"
            headers = {
                "Authorization": f"Bearer {os.getenv('LINE_CHANNEL_ACCESS_TOKEN')}"
            }
            response = requests.post(url, headers=headers)
            return response.status_code == 200
        except Exception as e:
            print(f"リッチメニュー設定エラー: {str(e)}")
            return False
    
    def _ensure_menus_exist(self):
        """必要なリッチメニューが存在することを確認し、なければ作成"""
        try:
            # リッチメニュー作成スクリプトを実行
            from app.features.linebot.rich_menu.create_menus import RichMenuCreator
            creator = RichMenuCreator()
            
            # 既存のメニューを確認
            menu_list = self._get_rich_menu_list()
            existing_menus = {}
            if menu_list and menu_list.get("richmenus"):
                for menu in menu_list["richmenus"]:
                    name = menu.get("name", "").lower()
                    existing_menus[name] = menu["richMenuId"]
            
            # 必要なメニューが存在するか確認
            required_menus = ["cast_menu", "customer_menu", "default"]
            menus_to_create = []
            
            for menu_type in required_menus:
                if menu_type not in existing_menus:
                    menus_to_create.append(menu_type)
            
            # 不足しているメニューを作成
            if menus_to_create:
                print(f"以下のメニューを作成します: {menus_to_create}")
                for menu_type in menus_to_create:
                    menu_id = creator.create_rich_menu(menu_type)
                    if menu_id:
                        # 画像のアップロードは一旦スキップ（プレースホルダー画像が必要）
                        print(f"メニュー作成成功: {menu_type} -> {menu_id}")
                    else:
                        print(f"メニュー作成失敗: {menu_type}")
            else:
                print("全ての必要なメニューが既に存在します")
                
        except Exception as e:
            print(f"メニュー作成エラー: {str(e)}")