# app/features/linebot/rich_menu/services/rich_menu_client.py

import requests
import os
from typing import Optional, Dict, Any, List
from app.core.config import LINE_CHANNEL_ACCESS_TOKEN

class RichMenuAPIClient:
    """LINE Rich Menu API クライアント"""
    
    BASE_URL = "https://api.line.me/v2/bot"
    
    def __init__(self):
        self.access_token = LINE_CHANNEL_ACCESS_TOKEN
        if not self.access_token.startswith("Bearer "):
            self.access_token = f"Bearer {self.access_token}"
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": self.access_token
        }
    
    def create_rich_menu(self, menu_payload: Dict[str, Any]) -> Optional[str]:
        """Rich Menuを作成"""
        try:
            url = f"{self.BASE_URL}/richmenu"
            response = requests.post(url, headers=self.headers, json=menu_payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("richMenuId")
            else:
                print(f"Rich Menu作成失敗: {response.status_code}, {response.text}")
                return None
                
        except Exception as e:
            print(f"Rich Menu作成エラー: {e}")
            return None
    
    def upload_rich_menu_image(self, rich_menu_id: str, image_path: str) -> bool:
        """Rich Menuに画像をアップロード"""
        try:
            if not os.path.exists(image_path):
                print(f"画像ファイルが見つかりません: {image_path}")
                return False
            
            url = f"{self.BASE_URL}/richmenu/{rich_menu_id}/content"
            headers = {
                "Authorization": self.access_token,
                "Content-Type": "image/png"
            }
            
            with open(image_path, 'rb') as image_file:
                response = requests.post(url, headers=headers, data=image_file, timeout=30)
            
            if response.status_code == 200:
                return True
            else:
                print(f"画像アップロード失敗: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            print(f"画像アップロードエラー: {e}")
            return False
    
    def set_user_rich_menu(self, user_id: str, rich_menu_id: str) -> bool:
        """ユーザーにRich Menuを適用"""
        try:
            url = f"{self.BASE_URL}/user/{user_id}/richmenu/{rich_menu_id}"
            response = requests.post(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"ユーザーメニュー設定失敗: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            print(f"ユーザーメニュー設定エラー: {e}")
            return False
    
    def get_user_rich_menu(self, user_id: str) -> Optional[str]:
        """ユーザーの現在のRich Menu IDを取得"""
        try:
            url = f"{self.BASE_URL}/user/{user_id}/richmenu"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("richMenuId")
            elif response.status_code == 404:
                # メニューが設定されていない
                return None
            else:
                print(f"ユーザーメニュー取得失敗: {response.status_code}, {response.text}")
                return None
                
        except Exception as e:
            print(f"ユーザーメニュー取得エラー: {e}")
            return None
    
    def unlink_user_rich_menu(self, user_id: str) -> bool:
        """ユーザーからRich Menuを削除"""
        try:
            url = f"{self.BASE_URL}/user/{user_id}/richmenu"
            response = requests.delete(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"ユーザーメニュー削除失敗: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            print(f"ユーザーメニュー削除エラー: {e}")
            return False
    
    def delete_rich_menu(self, rich_menu_id: str) -> bool:
        """Rich Menuを削除"""
        try:
            url = f"{self.BASE_URL}/richmenu/{rich_menu_id}"
            response = requests.delete(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"Rich Menu削除失敗: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            print(f"Rich Menu削除エラー: {e}")
            return False
    
    def list_rich_menus(self) -> List[Dict[str, Any]]:
        """Rich Menu一覧を取得"""
        try:
            url = f"{self.BASE_URL}/richmenu/list"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("richmenus", [])
            else:
                print(f"Rich Menu一覧取得失敗: {response.status_code}, {response.text}")
                return []
                
        except Exception as e:
            print(f"Rich Menu一覧取得エラー: {e}")
            return []