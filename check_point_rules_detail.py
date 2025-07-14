#!/usr/bin/env python3
"""ポイントルールの詳細確認スクリプト"""

from app.db.session import SessionLocal
from app.db.models.point import PointRule
from sqlalchemy import inspect
import json

def check_point_rules_detail():
    """ポイントルールの詳細を確認"""
    db = SessionLocal()
    try:
        # すべてのポイントルールを取得
        rules = db.query(PointRule).all()
        
        print(f"\n===== ポイントルール詳細 (全{len(rules)}件) =====\n")
        
        for rule in rules:
            print(f"ID: {rule.id}")
            print(f"ルール名: {rule.rule_name}")
            print(f"説明: {rule.rule_description}")
            print(f"イベントタイプ: {rule.event_type}")
            print(f"対象ユーザータイプ: {rule.target_user_type}")
            print(f"取引タイプ: {rule.transaction_type}")
            print(f"ポイントタイプ: {rule.point_type}")
            print(f"ポイント値: {rule.point_value}")
            print(f"加算フラグ: {rule.is_addition}")
            print(f"有効フラグ: {rule.is_active}")
            print(f"条件データ: {json.dumps(rule.condition_data, ensure_ascii=False) if rule.condition_data else 'なし'}")
            print(f"追加データ: {json.dumps(rule.additional_data, ensure_ascii=False) if rule.additional_data else 'なし'}")
            print(f"作成日時: {rule.created_at}")
            print("-" * 50)
        
        # Enumの値を確認
        print("\n===== Enum定義の確認 =====")
        mapper = inspect(PointRule)
        for column in mapper.columns:
            if hasattr(column.type, 'enums'):
                print(f"\n{column.name}の定義値:")
                for value in column.type.enums:
                    print(f"  - {value}")
                    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_point_rules_detail()