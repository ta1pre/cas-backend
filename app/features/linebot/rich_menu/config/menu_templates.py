# app/features/linebot/rich_menu/config/menu_templates.py

from app.features.linebot.rich_menu.models.menu_definition import RichMenuDefinition, MenuArea
from app.features.linebot.rich_menu.models.menu_condition import MenuType
import os

# 画像ファイルのベースパス（動的に取得）
def get_base_image_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "..", "assets", "static_images")

def get_menu_templates() -> dict:
    """全メニューテンプレートを取得"""
    
    base_image_path = get_base_image_path()
    
    return {
        MenuType.UNREGISTERED: RichMenuDefinition(
            name="未登録ユーザー",
            image_path=os.path.join(base_image_path, "unregistered.png"),
            areas=[
                # 1つの大きなボタン（全画面）
                MenuArea(
                    x=0, y=0, 
                    width=2500, height=1686,
                    uri="https://google.com"
                )
            ]
        ),
        
        MenuType.CUSTOMER_BASIC: RichMenuDefinition(
            name="ご利用者メニュー",
            image_path=os.path.join(base_image_path, "customer_basic.png"),
            areas=[
                # 2×2の4分割
                MenuArea(x=0, y=0, width=1250, height=843, uri="https://google.com"),      # 左上
                MenuArea(x=1250, y=0, width=1250, height=843, uri="https://google.com"),   # 右上  
                MenuArea(x=0, y=843, width=1250, height=843, uri="https://google.com"),    # 左下
                MenuArea(x=1250, y=843, width=1250, height=843, uri="https://google.com")  # 右下
            ]
        ),
        
        MenuType.CAST_BASIC: RichMenuDefinition(
            name="キャストメニュー",
            image_path=os.path.join(base_image_path, "cast_basic.png"),
            areas=[
                # 2×3の6分割
                MenuArea(x=0, y=0, width=833, height=843, uri="https://google.com"),       # 左上
                MenuArea(x=833, y=0, width=834, height=843, uri="https://google.com"),     # 中上
                MenuArea(x=1667, y=0, width=833, height=843, uri="https://google.com"),    # 右上
                MenuArea(x=0, y=843, width=833, height=843, uri="https://google.com"),     # 左下
                MenuArea(x=833, y=843, width=834, height=843, uri="https://google.com"),   # 中下  
                MenuArea(x=1667, y=843, width=833, height=843, uri="https://google.com")   # 右下
            ]
        )
    }

# Phase 2以降で追加予定のテンプレート
def get_future_templates() -> dict:
    """将来追加予定のメニューテンプレート"""
    
    base_image_path = get_base_image_path()
    
    return {
        MenuType.CAST_IDENTITY_REQUIRED: RichMenuDefinition(
            name="身分証アップロード要求",
            image_path=os.path.join(base_image_path, "cast_identity_required.png"),
            areas=[
                # 大きなメインボタン + 小さなサポートボタン
                MenuArea(x=0, y=0, width=2500, height=1200, uri="https://google.com"),     # メイン
                MenuArea(x=0, y=1200, width=1250, height=486, uri="https://google.com"),   # ヘルプ
                MenuArea(x=1250, y=1200, width=1250, height=486, uri="https://google.com") # サポート
            ]
        ),
        
        MenuType.CAST_BANK_REQUIRED: RichMenuDefinition(
            name="口座登録要求", 
            image_path=os.path.join(base_image_path, "cast_bank_required.png"),
            areas=[
                # 大きなメインボタン + 小さなサポートボタン
                MenuArea(x=0, y=0, width=2500, height=1200, uri="https://google.com"),     # メイン
                MenuArea(x=0, y=1200, width=1250, height=486, uri="https://google.com"),   # ヘルプ
                MenuArea(x=1250, y=1200, width=1250, height=486, uri="https://google.com") # サポート
            ]
        )
    }