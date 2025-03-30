# 予約確定時のポイント支払いルールを追加するスクリプト

from app.db.session import engine, SessionLocal
from sqlalchemy import text
from app.db.models.point import PointRule

def add_reservation_payment_rule():
    db = SessionLocal()
    try:
        # ルールが存在するか確認
        existing_rule = db.query(PointRule).filter(PointRule.rule_name == "reservation_payment").first()
        
        if not existing_rule:
            # 新しいルールを追加
            new_rule = PointRule(
                rule_name="reservation_payment",
                rule_description="予約確定時のポイント支払い",
                transaction_type="reservation_payment",
                point_type="regular",
                point_value=0,  # 実際の値は変数で渡す
                is_addition=False  # 減算（False）
            )
            db.add(new_rule)
            db.commit()
            print(f"✅ ルール '予約確定時のポイント支払い' を追加しました")
        else:
            print(f"✅ ルール '予約確定時のポイント支払い' は既に存在します")
            
    except Exception as e:
        db.rollback()
        print(f"エラーが発生しました: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_reservation_payment_rule()
