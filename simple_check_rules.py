#!/usr/bin/env python3
"""シンプルなポイントルール確認スクリプト"""

import sqlite3
import json

def check_rules():
    """SQLiteで直接ポイントルールを確認"""
    conn = sqlite3.connect('/Users/taichiumeki/project/sandbox/casqat.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # テーブル構造を確認
        cursor.execute("PRAGMA table_info(pnt_details_rules)")
        columns = cursor.fetchall()
        print("===== pnt_details_rules テーブル構造 =====")
        for col in columns:
            print(f"{col['name']} - {col['type']}")
        
        print("\n===== ポイントルールデータ =====")
        cursor.execute("SELECT * FROM pnt_details_rules ORDER BY id")
        rules = cursor.fetchall()
        
        for rule in rules:
            print(f"\nID: {rule['id']}")
            print(f"ルール名: {rule['rule_name']}")
            print(f"説明: {rule['rule_description']}")
            print(f"イベントタイプ: {rule['event_type']}")
            print(f"対象ユーザータイプ: {rule['target_user_type']}")
            print(f"取引タイプ: {rule['transaction_type']}")
            print(f"ポイントタイプ: {rule['point_type']}")
            print(f"ポイント値: {rule['point_value']}")
            print(f"加算フラグ: {rule['is_addition']}")
            print(f"有効フラグ: {rule['is_active']}")
            print(f"条件データ: {rule['condition_data']}")
            print(f"追加データ: {rule['additional_data']}")
            print(f"作成日時: {rule['created_at']}")
            print("-" * 50)
        
        print(f"\n総件数: {len(rules)}件")
        
        # 各カラムのユニーク値を確認
        print("\n===== 各カラムのユニーク値 =====")
        for col in ['point_type', 'target_user_type', 'transaction_type']:
            cursor.execute(f"SELECT DISTINCT {col} FROM pnt_details_rules")
            values = [row[0] for row in cursor.fetchall()]
            print(f"\n{col}の値: {values}")
            
    except Exception as e:
        print(f"エラー: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_rules()