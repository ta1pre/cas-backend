#!/usr/bin/env python3
# scripts/delete_all_menus.py

"""
全てのリッチメニューを削除するスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import requests

def main():
    print("全てのリッチメニューを削除します...")
    
    # 環境変数チェック
    token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    if not token:
        print("エラー: LINE_CHANNEL_ACCESS_TOKENが設定されていません")
        return
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 既存のメニューを確認
    print("\n既存のメニューを確認中...")
    response = requests.get("https://api.line.me/v2/bot/richmenu/list", headers=headers)
    
    if response.status_code != 200:
        print(f"メニュー一覧取得失敗: {response.status_code}")
        return
    
    menus = response.json().get("richmenus", [])
    print(f"既存のメニュー数: {len(menus)}")
    
    if len(menus) == 0:
        print("削除するメニューがありません")
        return
    
    # 各メニューを削除
    for menu in menus:
        menu_id = menu.get('richMenuId')
        menu_name = menu.get('name', 'unknown')
        print(f"\n削除中: {menu_name} (ID: {menu_id})")
        
        delete_url = f"https://api.line.me/v2/bot/richmenu/{menu_id}"
        delete_response = requests.delete(delete_url, headers=headers)
        
        if delete_response.status_code == 200:
            print(f"✓ 削除成功: {menu_name}")
        else:
            print(f"✗ 削除失敗: {menu_name} - {delete_response.status_code}")
    
    print("\n削除処理完了")

if __name__ == "__main__":
    main()