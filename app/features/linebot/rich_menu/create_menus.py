# app/features/linebot/rich_menu/create_menus.py

"""
リッチメニュー作成・管理モジュール

設定ベースでリッチメニューをLINEに登録します。
新しいメニュータイプは menu_config.py に設定を追加するだけで対応できます。
"""

import requests
import json
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from .menu_config import (
    get_menu_config,
    get_routing_map,
    MENU_CONFIGURATIONS
)

# .envファイルを明示的に読み込み
dotenv_path = os.path.join(os.path.dirname(__file__), "../../../../.env")
load_dotenv(dotenv_path)

# 環境に応じたAPI URLを設定
API_BASE_URL = os.getenv('FRONTEND_URL', 'https://cas.tokyo')

class RichMenuCreator:
    def __init__(self):
        self.access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.base_url = "https://api.line.me/v2/bot/richmenu"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def create_menu_config(self, menu_type: str) -> Dict[str, Any]:
        """
        メニュータイプに応じた設定を生成
        
        Args:
            menu_type: メニュータイプ
        
        Returns:
            Dict: LINE API用のメニュー設定
        """
        config = get_menu_config(menu_type)
        
        base_config = {
            "size": {
                "width": 2500,
                "height": 1686
            },
            "selected": True,
            "name": menu_type,
            "chatBarText": config.get('chat_bar_text', config['name']),
            "areas": self._get_menu_areas(menu_type)
        }
        return base_config
    
    def _get_user_type_from_menu_type(self, menu_type: str) -> str:
        """
        メニュータイプからユーザータイプを取得
        
        Args:
            menu_type: メニュータイプ
        
        Returns:
            str: ユーザータイプ（cast, customer, default）
        """
        if menu_type.startswith('cast'):
            return 'cast'
        elif menu_type.startswith('customer'):
            return 'customer'
        else:
            return 'default'
    
    def _get_menu_areas(self, menu_type: str) -> list:
        """
        メニュータイプに応じたエリア設定を返す
        
        Args:
            menu_type: メニュータイプ
        
        Returns:
            list: LINE API用のエリア設定
        """
        config = get_menu_config(menu_type)
        user_type = self._get_user_type_from_menu_type(menu_type)
        
        areas = []
        grid = config.get('grid', {'cols': 3, 'rows': 2})
        
        # グリッド設定に基づいてセルサイズを計算
        cell_width = 2500 // grid['cols']
        cell_height = 1686 // grid['rows']
        
        # 各アイテムのエリアを設定
        for idx, area in enumerate(config['areas']):
            position = area.get('position', idx)
            col = position % grid['cols']
            row = position // grid['cols']
            
            x = col * cell_width
            y = row * cell_height
            
            # 中央の列は幅を1増やす（端数調整）
            width = cell_width + 1 if col == 1 and grid['cols'] == 3 else cell_width
            
            area_config = {
                "bounds": {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": cell_height
                },
                "action": {
                    "type": "uri",
                    "uri": f"https://cas.tokyo/api/v1/r/{area['action']}?type={user_type}",
                    "label": f"{area.get('text', '')} {area.get('icon', '')}"
                }
            }
            areas.append(area_config)
        
        return areas
    
    def create_rich_menu(self, menu_type: str) -> Optional[str]:
        """リッチメニューを作成してメニューIDを返す"""
        try:
            config = self.create_menu_config(menu_type)
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=json.dumps(config)
            )
            
            if response.status_code == 200:
                menu_id = response.json().get("richMenuId")
                print(f"リッチメニュー作成成功: {menu_type} -> {menu_id}")
                return menu_id
            else:
                print(f"リッチメニュー作成失敗: {menu_type} -> {response.status_code} {response.text}")
                return None
                
        except Exception as e:
            print(f"リッチメニュー作成エラー: {menu_type} -> {str(e)}")
            return None
    
    def upload_image(self, menu_id: str, menu_type: str) -> bool:
        """リッチメニューに画像をアップロード"""
        try:
            from app.features.linebot.rich_menu.menu_designer import MenuDesigner
            import io
            
            # デザイナーで画像を生成
            designer = MenuDesigner()
            img = designer.create_menu_image(menu_type)
            
            # バイト配列に変換
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            url = f"https://api-data.line.me/v2/bot/richmenu/{menu_id}/content"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "image/png"
            }
            
            response = requests.post(
                url,
                headers=headers,
                data=img_byte_arr.getvalue()
            )
            
            if response.status_code == 200:
                print(f"画像アップロード成功: {menu_type}")
                return True
            else:
                print(f"画像アップロード失敗: {menu_type} -> {response.status_code}")
                return False
                
        except Exception as e:
            print(f"画像アップロードエラー: {menu_type} -> {str(e)}")
            return False
    
    def create_all_menus(self) -> Dict[str, str]:
        """
        全てのメニューを作成して、メニューIDのマップを返す
        
        Returns:
            Dict[str, str]: メニュータイプ -> メニューIDのマップ
        """
        # 設定に登録されているすべてのメニュータイプを取得
        menu_types = list(MENU_CONFIGURATIONS.keys())
        menu_ids = {}
        
        print(f"\n作成予定のメニュー: {menu_types}")
        
        for menu_type in menu_types:
            print(f"\n{'='*50}")
            print(f"メニュータイプ: {menu_type}")
            
            menu_id = self.create_rich_menu(menu_type)
            if menu_id:
                # 画像をアップロード
                if self.upload_image(menu_id, menu_type):
                    menu_ids[menu_type] = menu_id
                else:
                    # 画像アップロードに失敗した場合はメニューを削除
                    self.delete_rich_menu(menu_id)
        
        return menu_ids
    
    def delete_rich_menu(self, menu_id: str) -> bool:
        """リッチメニューを削除"""
        try:
            url = f"{self.base_url}/{menu_id}"
            response = requests.delete(url, headers=self.headers)
            return response.status_code == 200
        except:
            return False


# スタンドアロン実行用
if __name__ == "__main__":
    creator = RichMenuCreator()
    menu_ids = creator.create_all_menus()
    
    if menu_ids:
        print("\n作成されたメニューID:")
        for menu_type, menu_id in menu_ids.items():
            print(f"{menu_type}: {menu_id}")
        
        # 環境変数またはファイルに保存
        with open("/tmp/rich_menu_ids.json", "w") as f:
            json.dump(menu_ids, f, indent=2)
        print("\nメニューIDを /tmp/rich_menu_ids.json に保存しました")
    else:
        print("メニューの作成に失敗しました")