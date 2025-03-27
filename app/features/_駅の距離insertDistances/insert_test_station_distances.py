from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.session import SessionLocal
from app.db.models.station import Station
from app.db.models.station_distance import StationDistance
from pyproj import Geod
import time

# ✅ WGS84基準の測地線距離計算
geod = Geod(ellps="WGS84")

def calculate_distance(lat1, lon1, lat2, lon2):
    """ 精密な測地線距離を計算（pyprojを使用） """
    _, _, distance = geod.inv(lon1, lat1, lon2, lat2)
    return distance / 1000  # メートル → キロメートルに変換

def insert_test_station_distances():
    """ 🚆 **全駅**を対象に駅間距離を計算し登録（都道府県ごとに処理） """
    db: Session = SessionLocal()

    # ✅ すべての都道府県を取得
    prefecture_codes = db.query(Station.pref_cd).distinct().all()
    prefecture_codes = [p[0] for p in prefecture_codes]

    batch_size = 500  # バルクインサート用
    total_inserted = 0  # 登録件数カウント

    for pref_cd in prefecture_codes:
        print(f"🚀 処理開始: 都道府県コード {pref_cd}")

        # ✅ 都道府県ごとに駅を取得
        stations = db.query(Station).filter(Station.pref_cd == pref_cd).all()

        insert_data = []
        start_time = time.time()

        for i, s1 in enumerate(stations):
            for s2 in stations[i+1:]:  # ✅ 重複計算を避ける
                distance = calculate_distance(s1.lat, s1.lon, s2.lat, s2.lon)

                if distance < 10:  # ✅ 10km以内の駅のみ保存
                    # ✅ 既存データをチェック
                    exists = db.query(StationDistance).filter_by(
                        from_station_id=s1.id, to_station_id=s2.id
                    ).first()

                    if not exists:
                        insert_data.append({
                            "from_station_id": s1.id,
                            "to_station_id": s2.id,
                            "distance_km": distance
                        })

                # ✅ 500件ごとにバルクインサート
                if len(insert_data) >= batch_size:
                    try:
                        db.bulk_insert_mappings(StationDistance, insert_data)
                        db.commit()
                        total_inserted += len(insert_data)
                        print(f"✅ {len(insert_data)} 件登録 (累計: {total_inserted})")
                    except IntegrityError:
                        db.rollback()
                        print(f"⚠️ 重複エラー発生 → スキップ")
                    
                    insert_data = []

        # ✅ 残りのデータを保存
        if insert_data:
            db.bulk_insert_mappings(StationDistance, insert_data)
            db.commit()
            total_inserted += len(insert_data)
            print(f"✅ {len(insert_data)} 件登録 (累計: {total_inserted})")

        end_time = time.time()
        print(f"✅ 都道府県 {pref_cd} の処理完了: {end_time - start_time:.2f} 秒")

    db.close()
    print(f"🚀 全駅間のデータ登録完了！（合計 {total_inserted} 件）")

if __name__ == "__main__":
    insert_test_station_distances()
