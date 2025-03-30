# データベース情報確認スクリプト

from app.db.session import SessionLocal
from app.db.models.resv_reservation import ResvReservation
from app.db.models.point import PointTransaction, PointRule, PointBalance

def check_database():
    """データベース情報を確認する関数"""
    db = SessionLocal()
    try:
        # 予約情報の確認
        reservations = db.query(ResvReservation).limit(5).all()
        print("\n===== 予約情報 =====")
        for r in reservations:
            print(f"予約ID: {r.id}, ユーザーID: {r.user_id}, 合計ポイント: {r.total_points}")
        
        # ポイントルールの確認
        rules = db.query(PointRule).all()
        print("\n===== ポイントルール =====")
        for rule in rules:
            print(f"ルールID: {rule.id}, 名前: {rule.rule_name}, 値: {rule.point_value}, 加算: {rule.is_addition}")
        
        # 取引履歴の確認
        transactions = db.query(PointTransaction).order_by(PointTransaction.created_at.desc()).limit(10).all()
        print("\n===== 最近の取引履歴 =====")
        if transactions:
            for tx in transactions:
                print(f"ID: {tx.id}, ユーザー: {tx.user_id}, 変更: {tx.point_change}, 関連ID: {tx.related_id}, 説明: {tx.description}")
        else:
            print("取引履歴がありません")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
