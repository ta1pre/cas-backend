# ファイル: app/features/station/services/suggest_service.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models.station import Station
from app.db.models.line import Line
from typing import List

def suggest_stations(db: Session, query: str, limit: int = 10) -> List[dict]:
    """駅名の部分一致検索"""

    print(f"✅ 受け取ったクエリ: {query}")  # 🚀 どんなクエリが来ているか確認

    sql_query = (
        db.query(
            Station.id,
            Station.name,
            Line.line_name,
            Station.lat,
            Station.lon
        )
        .join(Line, Station.line_id == Line.id, isouter=True)
        .filter(Station.name.ilike(f"%{query}%"))  # ✅ 問題のフィルタ
        .limit(limit)
    )

    print(f"✅ 実行されるSQL: {str(sql_query)}")  # 🚀 実際にSQLAlchemyが生成するクエリを確認

    stations = sql_query.all()
    
    print(f"✅ クエリ結果: {stations}")

    if not stations:
        print("🚨 駅が見つかりません！")
        return []

    return [
        {
            "id": s.id,
            "name": s.name,
            "line_name": s.line_name if s.line_name else "不明",
            "distance_km": None,
            "line_id": None,
        }
        for s in stations
    ]
