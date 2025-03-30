# ポイントルールのデバッグスクリプト

from app.db.session import SessionLocal
from app.db.models.point import PointRule
import logging

logging.basicConfig(level=logging.INFO)

def check_point_rules():
    """ポイントルールの設定を確認する"""
    db = SessionLocal()
    try:
        # reservation_paymentルールの確認
        rule = db.query(PointRule).filter(PointRule.rule_name == "reservation_payment").first()
        
        if rule:
            print(f"\n===== 予約支払いルール確認 =====")
            print(f"ルールID: {rule.id}")
            print(f"ルール名: {rule.rule_name}")
            print(f"説明: {rule.rule_description}")
            print(f"取引タイプ: {rule.transaction_type}")
            print(f"ポイントタイプ: {rule.point_type}")
            print(f"ポイント値: {rule.point_value}")
            print(f"加算フラグ: {rule.is_addition}")
            print(f"作成日時: {rule.created_at}")
        else:
            print("\n⚠️ 予約支払いルール(reservation_payment)が見つかりません！")
            print("add_reservation_payment_rule.pyスクリプトを実行してルールを追加してください。")
            
        # 他のルールも確認
        all_rules = db.query(PointRule).all()
        print(f"\n===== 全ポイントルール ({len(all_rules)}件) =====")
        for r in all_rules:
            print(f"- {r.rule_name} (ID: {r.id}, 加算: {r.is_addition}, 値: {r.point_value})")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_point_rules()
