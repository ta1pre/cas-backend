# u30ddu30a4u30f3u30c8u652fu6255u3044u51e6u7406u306eu30c7u30d0u30c3u30b0u30b9u30afu30eau30d7u30c8

from app.db.session import SessionLocal
from app.features.reserve.change_status.confirmed.confirmed_service import run_action
from app.features.reserve.change_status.confirmed.confirmed_repository import get_user_points, get_reservation_total
from app.features.points.services.apply_point_rule_service import apply_point_rule
from app.db.models.point import PointTransaction, PointRule
import sys

def debug_point_payment(reservation_id, user_id):
    """u30ddu30a4u30f3u30c8u652fu6255u3044u51e6u7406u306eu30c7u30d0u30c3u30b0u3092u884cu3046u95a2u6570"""
    db = SessionLocal()
    try:
        print(f"\n\n===== u30c7u30d0u30c3u30b0u958bu59cb: u4e88u7d04ID {reservation_id}, u30e6u30fcu30b6u30fcID {user_id} =====")
        
        # u30e6u30fcu30b6u30fcu30ddu30a4u30f3u30c8u78bau8a8d
        user_points = get_user_points(db, user_id)
        print(f"\n1. u30e6u30fcu30b6u30fcu30ddu30a4u30f3u30c8u78bau8a8d: {user_points} u30ddu30a4u30f3u30c8")
        
        # u4e88u7d04u91d1u984du78bau8a8d
        total_points = get_reservation_total(db, reservation_id)
        print(f"2. u4e88u7d04u91d1u984du78bau8a8d: {total_points} u30ddu30a4u30f3u30c8")
        
        # u30ddu30a4u30f3u30c8u30ebu30fcu30ebu78bau8a8d
        rule = db.query(PointRule).filter(PointRule.rule_name == "reservation_payment").first()
        if rule:
            print(f"3. u30ddu30a4u30f3u30c8u30ebu30fcu30ebu78bau8a8d: {rule.rule_name} (u30ebu30fcu30ebID: {rule.id})")
        else:
            print(f"3. u30ddu30a4u30f3u30c8u30ebu30fcu30ebu78bau8a8d: u30ebu30fcu30ebu304cu898bu3064u304bu308au307eu305bu3093")
        
        # u624bu52d5u3067u30ddu30a4u30f3u30c8u652fu6255u3044u51e6u7406u3092u5b9fu884c
        print("\n4. u624bu52d5u3067u30ddu30a4u30f3u30c8u652fu6255u3044u51e6u7406u3092u5b9fu884c:")
        payment_result = apply_point_rule(
            db, 
            user_id, 
            "reservation_payment", 
            {
                "amount": -total_points,  # u30deu30a4u30cau30b9u5024u3068u3057u3066u6e21u3059
                "reservation_id": reservation_id,
                "description": f"u4e88u7d04ID:{reservation_id}u306eu30c7u30ddu30b8u30c3u30c8"
            }
        )
        print(f"   u7d50u679c: {payment_result}")
        
        # u53d6u5f15u5c65u6b74u78bau8a8d
        transactions = db.query(PointTransaction).filter(
            PointTransaction.user_id == user_id,
            PointTransaction.related_id == reservation_id
        ).all()
        
        print(f"\n5. u53d6u5f15u5c65u6b74u78bau8a8d: {len(transactions)} u4ef6u306eu53d6u5f15u304cu898bu3064u304bu308au307eu3057u305f")
        for i, tx in enumerate(transactions):
            print(f"   u53d6u5f15 {i+1}: ID={tx.id}, u91d1u984d={tx.point_change}, u8aacu660e={tx.description}, u6642u523b={tx.created_at}")
        
        print("\n===== u30c7u30d0u30c3u30b0u7d42u4e86 =====\n")
        
    except Exception as e:
        print(f"\nu30a8u30e9u30fcu304cu767au751fu3057u307eu3057u305f: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("u4f7fu3044u65b9: python debug_point_payment.py <u4e88u7d04ID> <u30e6u30fcu30b6u30fcID>")
        sys.exit(1)
    
    reservation_id = int(sys.argv[1])
    user_id = int(sys.argv[2])
    debug_point_payment(reservation_id, user_id)
