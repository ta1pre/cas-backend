# app/features/linebot/rich_menu/services/menu_manager.py

from typing import Optional, Dict, Any
from app.features.linebot.rich_menu.services.condition_engine import MenuConditionEngine
from app.features.linebot.rich_menu.services.rich_menu_client import RichMenuAPIClient
from app.features.linebot.rich_menu.services.image_service import MenuImageService
from app.features.linebot.rich_menu.config.menu_templates import get_menu_templates
from app.features.linebot.rich_menu.models.menu_condition import MenuType

class MenuManager:
    """Rich Menu管理の中心サービス"""
    
    def __init__(self):
        self.condition_engine = MenuConditionEngine()
        self.api_client = RichMenuAPIClient()
        self.image_service = MenuImageService()
        self.menu_templates = get_menu_templates()
        
        # Rich Menu IDキャッシュ（メニュータイプ -> Rich Menu ID）
        self._menu_cache = {}
    
    def update_user_menu(self, line_id: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """ユーザーのメニューを更新"""
        try:
            # 1. 適切なメニュータイプを決定
            menu_type = self.condition_engine.get_menu_type_for_user(user_info)
            
            # 2. 現在のユーザーメニューを確認
            current_menu_id = self.api_client.get_user_rich_menu(line_id)
            
            # 3. 必要なRich Menu IDを取得または作成
            target_menu_id = self._get_or_create_rich_menu(menu_type)
            
            if not target_menu_id:
                return {
                    "success": False,
                    "message": f"メニュー作成に失敗しました: {menu_type.value}",
                    "menu_type": menu_type.value
                }
            
            # 4. 既に同じメニューが適用されている場合はスキップ
            if current_menu_id == target_menu_id:
                return {
                    "success": True,
                    "message": "メニューは既に最新です",
                    "menu_type": menu_type.value,
                    "rich_menu_id": target_menu_id,
                    "changed": False
                }
            
            # 5. ユーザーにメニューを適用
            success = self.api_client.set_user_rich_menu(line_id, target_menu_id)
            
            if success:
                return {
                    "success": True,
                    "message": "メニューを更新しました",
                    "menu_type": menu_type.value,
                    "rich_menu_id": target_menu_id,
                    "previous_menu_id": current_menu_id,
                    "changed": True
                }
            else:
                return {
                    "success": False,
                    "message": "メニュー適用に失敗しました",
                    "menu_type": menu_type.value
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"メニュー更新エラー: {str(e)}",
                "error": str(e)
            }
    
    def _get_or_create_rich_menu(self, menu_type: MenuType) -> Optional[str]:
        """Rich Menu IDを取得または作成"""
        
        # キャッシュから確認
        if menu_type in self._menu_cache:
            menu_id = self._menu_cache[menu_type]
            # 実際にそのメニューが存在するか確認
            if self._verify_rich_menu_exists(menu_id):
                return menu_id
            else:
                # キャッシュから削除
                del self._menu_cache[menu_type]
        
        # 新規作成
        return self._create_rich_menu(menu_type)
    
    def _create_rich_menu(self, menu_type: MenuType) -> Optional[str]:
        """Rich Menuを新規作成"""
        
        if menu_type not in self.menu_templates:
            print(f"メニューテンプレートが見つかりません: {menu_type.value}")
            return None
        
        template = self.menu_templates[menu_type]
        
        # 1. Rich Menuを作成
        payload = template.to_create_payload()
        rich_menu_id = self.api_client.create_rich_menu(payload)
        
        if not rich_menu_id:
            print(f"Rich Menu作成失敗: {menu_type.value}")
            return None
        
        # 2. 画像をアップロード
        image_path = template.image_path
        
        # 画像が存在しない場合の処理
        if not self.image_service.image_exists(menu_type.value):
            print(f"警告: 画像ファイルが見つかりません: {image_path}")
            # デバッグ用として、とりあえずRich Menu IDを返す
            # 実際の運用では画像なしでは動作しない
            self._menu_cache[menu_type] = rich_menu_id
            return rich_menu_id
        
        upload_success = self.api_client.upload_rich_menu_image(rich_menu_id, image_path)
        
        if upload_success:
            # キャッシュに保存
            self._menu_cache[menu_type] = rich_menu_id
            return rich_menu_id
        else:
            # 画像アップロード失敗時はRich Menuを削除
            self.api_client.delete_rich_menu(rich_menu_id)
            print(f"画像アップロード失敗のためRich Menuを削除: {rich_menu_id}")
            return None
    
    def _verify_rich_menu_exists(self, rich_menu_id: str) -> bool:
        """Rich Menuが存在するか確認"""
        try:
            menus = self.api_client.list_rich_menus()
            return any(menu.get("richMenuId") == rich_menu_id for menu in menus)
        except:
            return False
    
    def get_user_menu_status(self, line_id: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """ユーザーのメニュー状態を取得（デバッグ用）"""
        try:
            # 期待されるメニュー
            expected_menu_type = self.condition_engine.get_menu_type_for_user(user_info)
            
            # 現在適用されているメニュー
            current_menu_id = self.api_client.get_user_rich_menu(line_id)
            
            # 条件デバッグ情報
            debug_info = self.condition_engine.debug_user_conditions(user_info)
            
            return {
                "line_id": line_id,
                "expected_menu_type": expected_menu_type.value,
                "current_menu_id": current_menu_id,
                "menu_cache": {k.value: v for k, v in self._menu_cache.items()},
                "condition_debug": debug_info,
                "available_images": self.image_service.list_available_images()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "line_id": line_id
            }
    
    def cleanup_unused_menus(self) -> Dict[str, Any]:
        """使用されていないRich Menuを削除（管理用）"""
        try:
            all_menus = self.api_client.list_rich_menus()
            cached_menu_ids = set(self._menu_cache.values())
            
            deleted_count = 0
            for menu in all_menus:
                menu_id = menu.get("richMenuId")
                if menu_id and menu_id not in cached_menu_ids:
                    if self.api_client.delete_rich_menu(menu_id):
                        deleted_count += 1
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "total_menus": len(all_menus)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }