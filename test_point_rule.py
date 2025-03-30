# u30ddu30a4u30f3u30c8u30ebu30fcu30ebu9069u7528u306eu30c6u30b9u30c8u30b9u30afu30eau30d7u30c8

from app.db.session import SessionLocal
from app.features.points.services.apply_point_rule_service import apply_point_rule
from app.db.models.point import PointTransaction, PointBalance
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_point_rule(user_id, amount, description):
    """u30ddu30a4u30f3u30c8u30ebu30fcu30ebu9069u7528u3092u30c6u30b9u30c8u3059u308bu95a2u6570"""
    db = SessionLocal()
    try:
        # u30e6u30fcu30b6u30fcu306eu30ddu30a4u30f3u30c8u6b8bu9ad8u78bau8a8d
        balance_before = db.query(PointBalance).filter(PointBalance.user_id == user_id).first()
        if balance_before:
            print(f"\n===== u9069u7528u524du306eu30ddu30a4u30f3u30c8u6b8bu9ad8 =====")
            print(f"u901au5e38u30ddu30a4u30f3u30c8: {balance_before.regular_point_balance}")
            print(f"u30dcu30fcu30cau30b9u30ddu30a4u30f3u30c8: {balance_before.bonus_point_balance}")
            print(f"u5408u8a08u30ddu30a4u30f3u30c8: {balance_before.total_point_balance}")
        else:
            print(f"\nu26a0ufe0f u30e6u30fcu30b6u30fcID {user_id} u306eu30ddu30a4u30f3u30c8u6b8bu9ad8u304cu898bu3064u304bu308au307eu305bu3093")
            print("u30c6u30b9u30c8u7528u306bu30ddu30a4u30f3u30c8u6b8bu9ad8u3092u4f5cu6210u3057u307eu3059...")
            new_balance = PointBalance(user_id=user_id, regular_point_balance=1000, bonus_point_balance=500, total_point_balance=1500)
            db.add(new_balance)
            db.commit()
            print("u30ddu30a4u30f3u30c8u6b8bu9ad8u3092u4f5cu6210u3057u307eu3057u305f: 1500u30ddu30a4u30f3u30c8")
            balance_before = new_balance
            
        # u30c7u30d0u30c3u30b0u7528u306bu30c8u30e9u30f3u30b6u30afu30b7u30e7u30f3u3092u958bu59cb
        db.begin()
        
        # u30ddu30a4u30f3u30c8u30ebu30fcu30ebu9069u7528u51e6u7406u3092u5b9fu884c
        print(f"\n===== u30ddu30a4u30f3u30c8u30ebu30fcu30ebu9069u7528u51e6u7406u5b9fu884c =====")
        print(f"u30ebu30fcu30eb: reservation_payment")
        print(f"u91d1u984d: {amount} u30ddu30a4u30f3u30c8")
        print(f"u8aacu660e: {description}")
        
        payment_result = apply_point_rule(
            db, 
            user_id, 
            "reservation_payment", 
            {
                "amount": amount,
                "reservation_id": 999,  # u30c6u30b9u30c8u7528u306eu4eeeu306eID
                "description": description
            }
        )
        
        print(f"\nu30ddu30a4u30f3u30c8u30ebu30fcu30ebu9069u7528u7d50u679c: {payment_result}")
        
        # u53d6u5f15u5c65u6b74u306eu78bau8a8d
        transactions = db.query(PointTransaction).filter(
            PointTransaction.user_id == user_id,
            PointTransaction.related_id == 999
        ).all()
        
        print(f"\n===== u53d6u5f15u5c65u6b74u78bau8a8d =====")
        if transactions:
            print(f"{len(transactions)}u4ef6u306eu53d6u5f15u304cu898bu3064u304bu308au307eu3057u305f")
            for i, tx in enumerate(transactions):
                print(f"\nu53d6u5f15 {i+1}:")
                print(f"  ID: {tx.id}")
                print(f"  u30e6u30fcu30b6u30fcID: {tx.user_id}")
                print(f"  u30ebu30fcu30ebID: {tx.rule_id}")
                print(f"  u95a2u9023ID: {tx.related_id}")
                print(f"  u95a2u9023u30c6u30fcu30d6u30eb: {tx.related_table}")
                print(f"  u53d6u5f15u30bfu30a4u30d7: {tx.transaction_type}")
                print(f"  u30ddu30a4u30f3u30c8u5909u66f4: {tx.point_change}")
                print(f"  u30ddu30a4u30f3u30c8u30bdu30fcu30b9: {tx.point_source}")
                print(f"  u53d6u5f15u5f8cu6b8bu9ad8: {tx.balance_after}")
                print(f"  u8aacu660e: {tx.description}")
                print(f"  u4f5cu6210u65e5u6642: {tx.created_at}")
        else:
            print("u53d6u5f15u5c65u6b74u304cu898bu3064u304bu308au307eu305bu3093uff01")
            
        # u5909u66f4u5f8cu306eu30ddu30a4u30f3u30c8u6b8bu9ad8u78bau8a8d
        balance_after = db.query(PointBalance).filter(PointBalance.user_id == user_id).first()
        if balance_after:
            print(f"\n===== u9069u7528u5f8cu306eu30ddu30a4u30f3u30c8u6b8bu9ad8 =====")
            print(f"u901au5e38u30ddu30a4u30f3u30c8: {balance_after.regular_point_balance}")
            print(f"u30dcu30fcu30cau30b9u30ddu30a4u30f3u30c8: {balance_after.bonus_point_balance}")
            print(f"u5408u8a08u30ddu30a4u30f3u30c8: {balance_after.total_point_balance}")
            
        # u30c7u30d0u30c3u30b0u7528u306bu30b3u30dfu30c3u30c8u3059u308bu304bu78bau8a8d
        commit = input("\nu5909u66f4u3092u30c7u30fcu30bfu30d9u30fcu30b9u306bu53cdu6620u3057u307eu3059u304buff1f (y/n): ")
        if commit.lower() == 'y':
            db.commit()
            print("u5909u66f4u3092u30c7u30fcu30bfu30d9u30fcu30b9u306bu53cdu6620u3057u307eu3057u305f")
        else:
            db.rollback()
            print("u5909u66f4u3092u30edu30fcu30ebu30d0u30c3u30afu3057u307eu3057u305f")
            
    except Exception as e:
        db.rollback()
        print(f"\nu30a8u30e9u30fcu304cu767au751fu3057u307eu3057u305f: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("u4f7fu3044u65b9: python test_point_rule.py <u30e6u30fcu30b6u30fcID> <u91d1u984d> <u8aacu660e>")
        print("u4f8b: python test_point_rule.py 1 -100 'u4e88u7d04ID:999u306eu30c7u30ddu30b8u30c3u30c8'")
        sys.exit(1)
    
    user_id = int(sys.argv[1])
    amount = int(sys.argv[2])
    description = sys.argv[3]
    test_point_rule(user_id, amount, description)
