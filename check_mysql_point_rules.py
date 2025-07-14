#!/usr/bin/env python3
"""MySQLデータベースのポイントルールを直接確認"""

import os
from dotenv import load_dotenv
import pymysql
from datetime import datetime

# .envファイルから環境変数を読み込む
load_dotenv()

def check_mysql_point_rules():
    """MySQLでポイントルールを確認"""
    # DATABASE_URLから接続情報を解析
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URLが設定されていません")
        return
    
    # URLを解析
    # mysql+pymysql://username:password@host/database
    import re
    match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@([^/]+)/(.+)', db_url)
    if not match:
        print("DATABASE_URLの形式が正しくありません")
        return
    
    user, password, host, database = match.groups()
    
    connection = None
    try:
        # MySQLに接続
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # テーブル構造を確認
            cursor.execute("DESCRIBE pnt_details_rules")
            columns = cursor.fetchall()
            print("===== pnt_details_rules テーブル構造 =====")
            for col in columns:
                print(f"{col['Field']} - {col['Type']} - {col['Null']} - {col['Default']}")
            
            # ポイントルールデータを取得
            cursor.execute("SELECT * FROM pnt_details_rules ORDER BY id")
            rules = cursor.fetchall()
            
            print(f"\n===== ポイントルールデータ (全{len(rules)}件) =====")
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
            
            # 各カラムのユニーク値を確認
            print("\n===== 各カラムのユニーク値 =====")
            for col in ['point_type', 'target_user_type', 'transaction_type']:
                cursor.execute(f"SELECT DISTINCT {col} FROM pnt_details_rules")
                values = [row[col] for row in cursor.fetchall()]
                print(f"\n{col}の値: {values}")
                
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    check_mysql_point_rules()