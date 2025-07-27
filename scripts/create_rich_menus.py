#!/usr/bin/env python3
# scripts/create_rich_menus.py

"""
リッチメニューを作成するスクリプト
管理画面で作成したメニューの代わりにAPIで直接作成
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.features.linebot.rich_menu.create_menus import RichMenuCreator

def main():
    print("リッチメニュー作成を開始します...")
    
    # 環境変数チェック
    token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    if not token:
        print("エラー: LINE_CHANNEL_ACCESS_TOKENが設定されていません")
        return
    
    print(f"トークン確認: {token[:10]}...")
    
    # リッチメニュー作成
    creator = RichMenuCreator()
    
    # 既存のメニューを確認
    print("\n既存のメニューを確認中...")
    import requests
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get("https://api.line.me/v2/bot/richmenu/list", headers=headers)
    
    if response.status_code == 200:
        menus = response.json().get("richmenus", [])
        print(f"既存のメニュー数: {len(menus)}")
        for menu in menus:
            print(f"  - {menu.get('name', 'unknown')} (ID: {menu.get('richMenuId')})")
    else:
        print(f"メニュー一覧取得失敗: {response.status_code}")
    
    # 新しいメニューを作成
    print("\n新しいメニューを作成中...")
    menu_types = ["cast_menu", "customer_menu", "default"]
    created_menus = {}
    
    for menu_type in menu_types:
        print(f"\n{menu_type}を作成中...")
        menu_id = creator.create_rich_menu(menu_type)
        if menu_id:
            created_menus[menu_type] = menu_id
            print(f"✓ {menu_type}: {menu_id}")
        else:
            print(f"✗ {menu_type}: 作成失敗")
    
    if created_menus:
        print(f"\n作成成功: {len(created_menus)}個のメニュー")
        print("\nメニューID一覧:")
        for menu_type, menu_id in created_menus.items():
            print(f"  {menu_type}: {menu_id}")
    else:
        print("\nメニューの作成に失敗しました")

if __name__ == "__main__":
    main()