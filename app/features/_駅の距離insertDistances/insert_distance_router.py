from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from .insert_test_station_distances import insert_test_station_distances

# ✅ ルーター作成
insert_distance_router = APIRouter(
    prefix="/insert-distance",
    tags=["Insert Distance"]
)

@insert_distance_router.post("/test")
def add_test_distances(db: Session = Depends(get_db)):
    """ 🚆 2駅を起点とした駅間距離データを一括登録（テスト用） """
    insert_test_station_distances()
    return {"message": "🚀 2駅を起点とした駅間距離データの登録が完了しました！"}
