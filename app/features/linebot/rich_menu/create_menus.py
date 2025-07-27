# app/features/linebot/rich_menu/create_menus.py

import requests
import json
import os
from typing import Dict, Any, Optional

class RichMenuCreator:
    def __init__(self):
        self.access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.base_url = "https://api.line.me/v2/bot/richmenu"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def create_menu_config(self, menu_type: str) -> Dict[str, Any]:
        """メニュータイプに応じた設定を生成"""
        base_config = {
            "size": {
                "width": 2500,
                "height": 1686
            },
            "selected": True,
            "name": menu_type,
            "chatBarText": self._get_chat_bar_text(menu_type),
            "areas": self._get_menu_areas(menu_type)
        }
        return base_config
    
    def _get_chat_bar_text(self, menu_type: str) -> str:
        """メニュータイプに応じたチャットバーテキストを返す"""
        texts = {
            "cast_menu": "キャストメニュー",
            "customer_menu": "カスタマーメニュー",
            "default": "メニュー"
        }
        return texts.get(menu_type, "メニュー")
    
    def _get_menu_areas(self, menu_type: str) -> list:
        """メニュータイプに応じたエリア設定を返す"""
        if menu_type == "cast_menu":
            return [
                {
                    "bounds": {"x": 0, "y": 0, "width": 833, "height": 843},
                    "action": {"type": "uri", "uri": "https://precas.jp/api/v1/account/line/login?tr=menu_cast"}
                },
                {
                    "bounds": {"x": 833, "y": 0, "width": 834, "height": 843},
                    "action": {"type": "uri", "uri": "https://precas.jp/cast/earnings"}
                },
                {
                    "bounds": {"x": 1667, "y": 0, "width": 833, "height": 843},
                    "action": {"type": "uri", "uri": "https://precas.jp/cast/profile"}
                },
                {
                    "bounds": {"x": 0, "y": 843, "width": 833, "height": 843},
                    "action": {"type": "uri", "uri": "https://precas.jp/cast/messages"}
                },
                {
                    "bounds": {"x": 833, "y": 843, "width": 834, "height": 843},
                    "action": {"type": "uri", "uri": "https://precas.jp/cast/settings"}
                },
                {
                    "bounds": {"x": 1667, "y": 843, "width": 833, "height": 843},
                    "action": {"type": "message", "text": "ヘルプ"}
                }
            ]
        elif menu_type == "customer_menu":
            return [
                {
                    "bounds": {"x": 0, "y": 0, "width": 833, "height": 843},
                    "action": {"type": "uri", "uri": "https://precas.jp/api/v1/account/line/login?tr=menu_customer"}
                },
                {
                    "bounds": {"x": 833, "y": 0, "width": 834, "height": 843},
                    "action": {"type": "uri", "uri": "https://precas.jp/favorites"}
                },
                {
                    "bounds": {"x": 1667, "y": 0, "width": 833, "height": 843},
                    "action": {"type": "uri", "uri": "https://precas.jp/reservations"}
                },
                {
                    "bounds": {"x": 0, "y": 843, "width": 833, "height": 843},
                    "action": {"type": "uri", "uri": "https://precas.jp/history"}
                },
                {
                    "bounds": {"x": 833, "y": 843, "width": 834, "height": 843},
                    "action": {"type": "uri", "uri": "https://precas.jp/profile"}
                },
                {
                    "bounds": {"x": 1667, "y": 843, "width": 833, "height": 843},
                    "action": {"type": "message", "text": "お問い合わせ"}
                }
            ]
        else:  # default
            return [
                {
                    "bounds": {"x": 0, "y": 0, "width": 1250, "height": 843},
                    "action": {"type": "uri", "uri": "https://precas.jp/api/v1/account/line/login?tr=menu_default"}
                },
                {
                    "bounds": {"x": 1250, "y": 0, "width": 1250, "height": 843},
                    "action": {"type": "uri", "uri": "https://precas.jp/about"}
                },
                {
                    "bounds": {"x": 0, "y": 843, "width": 1250, "height": 843},
                    "action": {"type": "uri", "uri": "https://precas.jp/howto"}
                },
                {
                    "bounds": {"x": 1250, "y": 843, "width": 1250, "height": 843},
                    "action": {"type": "message", "text": "利用規約"}
                }
            ]
    
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
        """リッチメニューに画像をアップロード（プレースホルダー画像）"""
        try:
            # 実際の実装では適切な画像ファイルを使用
            # ここではプレースホルダーとして単色画像を生成
            from PIL import Image
            import io
            
            # 2500x1686の画像を生成
            colors = {
                "cast_menu": (255, 200, 200),  # 薄い赤
                "customer_menu": (200, 200, 255),  # 薄い青
                "default": (200, 255, 200)  # 薄い緑
            }
            color = colors.get(menu_type, (220, 220, 220))
            
            img = Image.new('RGB', (2500, 1686), color=color)
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
        """全てのメニューを作成して、メニューIDのマップを返す"""
        menu_types = ["cast_menu", "customer_menu", "default"]
        menu_ids = {}
        
        for menu_type in menu_types:
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