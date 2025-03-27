from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from app.db.models.station import Station
from app.db.models.line import Line
from app.db.models.resv_reservation import ResvReservation
from app.features.reserve.schemas.cast.cast_station_schema import StationSuggestResponse

def suggest_stations(db: Session, query: str) -> List[StationSuggestResponse]:
    """駅名のサジェストを行う"""
    # 駅と路線を結合して取得
    stations = db.query(Station, Line.line_name).join(
        Line, Station.line_id == Line.id
    ).filter(
        Station.name.ilike(f"%{query}%")
    ).all()
    
    # 駅名でグループ化
    station_groups = {}
    for station, line_name in stations:
        if station.name not in station_groups:
            station_groups[station.name] = {
                'ids': [station.id],
                'line_names': [line_name] if line_name else []
            }
        else:
            station_groups[station.name]['ids'].append(station.id)
            if line_name:
                station_groups[station.name]['line_names'].append(line_name)
    
    # レスポンスの作成
    result = []
    for name, data in station_groups.items():
        if len(data['ids']) == 1:
            # 単一の駅の場合
            result.append(StationSuggestResponse(
                id=data['ids'][0],
                name=name,
                line_name=data['line_names'][0] if data['line_names'] else None
            ))
        else:
            # 複数の駅が存在する場合
            result.append(StationSuggestResponse(
                id=data['ids'][0],  # 最初のIDを使用
                name=name,
                line_name="複数乗り入れ"
            ))
    
    return result[:10]  # 最大10件まで返す

def update_station(db: Session, reservation_id: int, cast_id: int, station_id: int | None) -> bool:
    """予約の駅情報を更新する"""
    reservation = db.query(ResvReservation).filter(
        ResvReservation.id == reservation_id,
        ResvReservation.cast_id == cast_id
    ).first()
    
    if not reservation:
        return False
        
    if station_id:
        # 駅の存在確認
        station = db.query(Station).filter(Station.id == station_id).first()
        if not station:
            return False
            
    reservation.location = str(station_id) if station_id else None
    db.commit()
    
    return True
