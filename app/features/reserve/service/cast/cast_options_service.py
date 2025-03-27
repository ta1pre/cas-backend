# 📂 app/features/reserve/service/cast/cast_options_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.features.reserve.schemas.cast.cast_options_schema import (
    CastOptionRequest,
    CastOptionResponse,
    SelectedOption
)
from app.features.reserve.repositories.cast.cast_options_repository import (
    get_available_options_for_cast,
    get_selected_options_by_reservation,
    check_belongs_to_cast
)
from app.db.models.station import Station

def get_cast_options(db: Session, req: CastOptionRequest) -> CastOptionResponse:
    """
    キャストが予約に対して利用可能なオプション一覧 & 現在選択中のオプションをまとめて返す
    """
    # 予約がcast_idに属しているか確認
    belongs = check_belongs_to_cast(db, req.reservation_id, req.cast_id)
    if not belongs:
        raise HTTPException(status_code=404, detail="該当の予約が見つかりません")

    # 1) キャストが対応可能なオプション(マスター)
    available = get_available_options_for_cast(db, req.cast_id)

    # 2) この予約に紐づくオプション
    selected = get_selected_options_by_reservation(db, req.reservation_id)

    # 駅IDから駅名を取得する辞書を作成
    station_dict = {}
    for row in selected:
        if row.option_id:
            station = db.query(Station).filter(Station.id == row.option_id).first()
            if station:
                station_dict[row.option_id] = station.name

    # 変換: pydanticへ渡す
    available_options = [
        {
            "option_id": row.option_id,
            "option_name": row.option_name,
            "option_price": row.option_price
        }
        for row in available
    ]

    selected_options = []
    for row in selected:
        # マスターオプションの場合
        if row.option_id:
            option_data = {
                "option_id": row.option_id
            }
            # 駅IDの場合は駅名も追加
            if row.option_id in station_dict:
                option_data["station_name"] = station_dict[row.option_id]
            selected_options.append(option_data)
        # 自由入力オプションの場合
        elif row.custom_name:  
            selected_options.append({
                "custom_option_name": row.custom_name,  
                "custom_option_price": row.option_price
            })

    return CastOptionResponse(
        available_options=available_options,
        selected_options=selected_options
    )
