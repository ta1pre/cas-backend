# scripts/update_rich_menu.py

"""
リッチメニュー更新スクリプト

使用方法:
1. 新しいリッチメニューを作成
2. 画像をアップロード  
3. 特定ユーザーに適用

実行例:
python scripts/update_rich_menu.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.features.linebot.rich_menu.create_menus import RichMenuCreator
from app.features.linebot.rich_menu.services.rich_menu_client import RichMenuAPIClient
from app.features.linebot.rich_menu.menu_designer import MenuDesigner

def main():
    print("=== リッチメニュー更新スクリプト ===")
    
    # 1. 新しいメニューを作成
    print("\n1. 新しいリッチメニューを作成中...")
    creator = RichMenuCreator()
    
    # すべてのメニュータイプを更新
    menu_types = ['cast_menu', 'cast_unverified_menu', 'customer_menu', 'default']
    created_menus = {}
    
    for menu_type in menu_types:
        print(f"  {menu_type} を作成中...")
        menu_id = creator.create_rich_menu(menu_type)
        if menu_id:
            created_menus[menu_type] = menu_id
            print(f"  ✅ 作成成功: {menu_id}")
        else:
            print(f"  ❌ 作成失敗: {menu_type}")
    
    # 2. 画像を生成・アップロード
    print("\n2. 画像をアップロード中...")
    designer = MenuDesigner()
    client = RichMenuAPIClient()
    
    os.makedirs('/tmp/rich_menu_update', exist_ok=True)
    
    for menu_type, menu_id in created_menus.items():
        print(f"  {menu_type} の画像をアップロード中...")
        
        # 画像を生成
        img = designer.create_menu_image(menu_type)
        image_path = f'/tmp/rich_menu_update/{menu_type}.png'
        img.save(image_path)
        
        # アップロード
        success = client.upload_rich_menu_image(menu_id, image_path)
        if success:
            print(f"  ✅ アップロード成功: {menu_type}")
        else:
            print(f"  ❌ アップロード失敗: {menu_type}")
    
    # 3. 結果表示
    print("\n3. 結果:")
    print("新しく作成されたリッチメニュー:")
    for menu_type, menu_id in created_menus.items():
        print(f"  {menu_type}: {menu_id}")
    
    print("\n⚠️  ユーザーへの適用は実際のLINEユーザーIDが必要です")
    print("適用方法: client.set_user_rich_menu(user_id, menu_id)")
    
    # クリーンアップ
    print("\n4. 一時ファイルを削除...")
    import shutil
    if os.path.exists('/tmp/rich_menu_update'):
        shutil.rmtree('/tmp/rich_menu_update')
        print("✅ クリーンアップ完了")

if __name__ == "__main__":
    main()