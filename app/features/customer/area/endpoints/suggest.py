from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..service.suggest_service import suggest_stations
from ..schemas.suggest_schemas import StationSuggestResponse
from pydantic import BaseModel  # ✅ 追加
from app.db.session import get_db
from ..service.station_service import fetch_current_station
from ..schemas.station_schema import StationResponse

router = APIRouter()

# ✅ 正しいリクエストスキーマを定義
class StationSuggestRequest(BaseModel):
    query: str

@router.post("/station/suggest", response_model=List[StationSuggestResponse])
def get_suggested_stations(request: StationSuggestRequest, db: Session = Depends(get_db)):
    """駅名の部分一致検索を行い、固定データを返す（デバッグ用）"""
    
    print("✅ /station/suggest が呼ばれました:", request.query)  # ログ出力

    return suggest_stations(db, request.query)

