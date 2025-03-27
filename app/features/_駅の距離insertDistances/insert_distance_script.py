# ✅ app/features/insertDistances/insert_distance_script.py
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from .repositories.insert_distance import insert_one_distance

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))



def main():
    db: Session = SessionLocal()
    
    # ✅ 仮の駅IDと距離
    from_station_id = 101
    to_station_id = 102
    distance_km = 5.2

    try:
        new_distance = insert_one_distance(db, from_station_id, to_station_id, distance_km)
        print(f"✅ 追加成功: {new_distance.id} ({from_station_id} → {to_station_id}, {distance_km} km)")
    except Exception as e:
        print(f"❌ エラー: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
