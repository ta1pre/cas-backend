# app/features/linebot/rich_menu/services/image_service.py

import os
from typing import Optional

class MenuImageService:
    """メニュー画像管理サービス"""
    
    def __init__(self):
        # 相対パスに変更（実行環境に依存しない）
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.join(current_dir, "..", "assets", "static_images")
    
    def get_image_path(self, menu_type: str) -> Optional[str]:
        """メニュータイプに対応する画像パスを取得"""
        image_filename = f"{menu_type}.png"
        image_path = os.path.join(self.base_path, image_filename)
        
        # 開発中は画像ファイルがない場合があるので、存在チェックなしで返す
        return image_path
    
    def image_exists(self, menu_type: str) -> bool:
        """画像ファイルが存在するかチェック"""
        image_path = self.get_image_path(menu_type)
        return os.path.exists(image_path) if image_path else False
    
    def list_available_images(self) -> list:
        """利用可能な画像一覧を取得"""
        if not os.path.exists(self.base_path):
            return []
        
        images = []
        for filename in os.listdir(self.base_path):
            if filename.endswith('.png'):
                menu_type = filename.replace('.png', '')
                images.append({
                    'menu_type': menu_type,
                    'filename': filename,
                    'path': os.path.join(self.base_path, filename)
                })
        
        return images
    
    def get_placeholder_info(self, menu_type: str) -> dict:
        """画像が存在しない場合のプレースホルダー情報"""
        return {
            'menu_type': menu_type,
            'expected_path': self.get_image_path(menu_type),
            'exists': self.image_exists(menu_type),
            'message': f'{menu_type}.png をアップロードしてください'
        }