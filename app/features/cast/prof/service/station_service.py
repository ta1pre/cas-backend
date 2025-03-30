# 駅情報サービス (キャストプロフィール用)
from sqlalchemy.orm import Session
from app.db.models.station import Station
from typing import Optional

def get_station_by_id(db: Session, station_id: int) -> Optional[Station]:
    """駅IDから駅情報を取得する"""
    try:
        # 数値に変換可能な場合のみクエリを実行
        if station_id and isinstance(station_id, (int, str)):
            station_id_int = int(station_id) if isinstance(station_id, str) else station_id
            return db.query(Station).filter(Station.id == station_id_int).first()
    except (ValueError, TypeError):
        # 変換できない場合やNoneの場合はNoneを返す
        pass
    return None
