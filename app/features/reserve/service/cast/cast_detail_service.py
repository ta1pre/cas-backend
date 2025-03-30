# 📂 app/features/reserve/service/cast/cast_detail_service.py

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.models.resv_reservation import ResvReservation
from app.db.models.user import User
from app.db.models.point_details import PointDetailsCourse, PointDetailsOption
from app.db.models.resv_reservation_option import ResvReservationOption
from app.db.models.station import Station
from app.db.models.cast_common_prof import CastCommonProf
from app.db.models.resv_status_detail import ResvStatusDetail # 追加: ResvStatusDetailをインポート
from app.features.reserve.schemas.cast.cast_detail_schema import CastReservationDetailResponse, OptionDetail
from fastapi import HTTPException

def get_reservation_detail(db: Session, reservation_id: int, cast_id: int) -> CastReservationDetailResponse:
    """
    キャスト用予約詳細取得サービス
    
    返り値:
    {
        "reservation_id": int,
        "user_name": str,
        "course_id": int,
        "course_name": str,
        "start_time": datetime,
        "end_time": datetime,
        "location": str,
        "station_name": str,  # 最寄り駅名
        "latitude": float,
        "longitude": float,
        
        # 料金情報
        "designation_fee": int,  # 指名料 (0固定、DBに存在しないため)
        "options_fee": int,      # オプション料金合計
        "traffic_fee": int,      # 交通費
        "reservation_fee": int,  # 予約基本料金
        "course_fee": int,       # コース料金（キャスト報酬）
        "total_points": int,     # 合計金額（ポイント）
        
        # オプション詳細
        "options": [
            {
                "option_id": int,
                "name": str,
                "price": int,
                "is_custom": bool
            },
            ...
        ],
        
        "status": str,
        "cast_label": str,
        "description": str,
        "color_code": str,
        "reservation_note": str,
        "cancel_reason": str
    }
    """
    # 基本予約情報の取得
    stmt = (
        select(
            ResvReservation.id.label("reservation_id"),
            User.nick_name.label("user_name"),
            ResvReservation.course_id, # 追加
            PointDetailsCourse.course_name,
            PointDetailsCourse.cast_reward_points.label("course_fee"),  # コース料金（キャスト報酬）
            ResvReservation.start_time,
            ResvReservation.end_time,
            ResvReservation.location,  # location は station id
            Station.name.label("station_name"),  # stationsテーブルから駅名を取得
            ResvReservation.latitude,
            ResvReservation.longitude,
            ResvReservation.traffic_fee,
            ResvReservation.reservation_fee,
            ResvReservation.total_points,
            ResvReservation.status,
            ResvStatusDetail.cast_label,  # 追加: キャスト向け表示文言
            ResvStatusDetail.description, # 追加: ステータスの説明
            ResvReservation.reservation_note,
            ResvReservation.cancel_reason,
            CastCommonProf.reservation_fee.label("designation_fee"),  # 指名料をキャストプロフィールから取得
            ResvStatusDetail.color_code # 追加: color_code を取得
        )
        .join(User, ResvReservation.user_id == User.id)
        .join(PointDetailsCourse, ResvReservation.course_id == PointDetailsCourse.id)
        .join(CastCommonProf, ResvReservation.cast_id == CastCommonProf.cast_id)  # キャストプロフィールと結合
        .join(Station, ResvReservation.location == Station.id)  # stationsテーブルと結合
        .join(ResvStatusDetail, ResvReservation.status == ResvStatusDetail.status_key) # 追加: ResvStatusDetailと結合
        .where(ResvReservation.id == reservation_id, ResvReservation.cast_id == cast_id)
    )

    reservation = db.execute(stmt).mappings().first()

    if not reservation:
        raise HTTPException(status_code=404, detail="予約が見つかりません")
    

    
    # オプション情報の取得
    options_query = (
        db.query(
            ResvReservationOption.option_id,
            ResvReservationOption.custom_name,
            ResvReservationOption.option_price,
        )
        .filter(
            ResvReservationOption.reservation_id == reservation_id,
            ResvReservationOption.status == "active"  # アクティブなオプションのみ取得
        )
        .all()
    )
    
    # オプション料金の計算とオプション情報の収集
    options = []
    options_fee = 0
    
    for option in options_query:
        # カスタムオプションかどうかは、option_id == 0 で判断
        is_custom = option.option_id == 0
        
        price = 0
        name = ""
        
        if is_custom:
            # カスタムオプションの場合
            name = option.custom_name
            price = option.option_price if option.option_price is not None else 0
        else:
            # 通常オプションの場合、マスターテーブルからデータを取得
            try:
                option_master = db.query(PointDetailsOption).get(option.option_id)
                if option_master:
                    name = option_master.option_name
                    # マスターテーブルの価格を使用
                    price = option_master.price
                else:
                    name = f"オプション{option.option_id}"
                    price = option.option_price if option.option_price is not None else 0
            except Exception as e:
                print(f"DEBUG - オプションマスター取得エラー: {e}")
                name = f"オプション{option.option_id}"
                price = option.option_price if option.option_price is not None else 0
        
        print(f"DEBUG - オプション処理: option_id={option.option_id}, name={name}, price={price}, is_custom={is_custom}")
        
        # オプション情報をリストに追加
        option_detail = OptionDetail(
            option_id=option.option_id,
            name=name,
            price=price,
            is_custom=is_custom
        )
        options.append(option_detail)
        
        # 合計金額に加算
        options_fee += price
    
    print(f"DEBUG - オプション処理完了: 合計{options_fee}円、{len(options)}件のオプション")
    
    # 指名料とコース料金を取得
    designation_fee = reservation.get("designation_fee") or 0
    course_fee = reservation.get("course_fee") or 0
    
    print(f"DEBUG - 料金情報:")
    print(f"  - 指名料: {designation_fee}")
    print(f"  - コース料金（キャスト報酬）: {course_fee}")
    
    # レスポンスの構築
    response = CastReservationDetailResponse(
        reservation_id=reservation["reservation_id"],
        user_name=reservation["user_name"],
        course_id=reservation["course_id"], # 追加
        course_name=reservation["course_name"],
        start_time=reservation["start_time"],
        end_time=reservation["end_time"],
        location=reservation["location"], # location は station id
        station_name=reservation["station_name"], # stationsテーブルから取得した駅名
        latitude=reservation["latitude"],
        longitude=reservation["longitude"],
        
        # 料金情報
        designation_fee=designation_fee,  # 指名料（キャストプロフィールから）
        options_fee=options_fee,  # オプション料金合計
        traffic_fee=reservation["traffic_fee"],  # 交通費
        reservation_fee=reservation["reservation_fee"],  # 予約基本料金
        course_fee=course_fee,  # コース料金（キャスト報酬）
        total_points=reservation["total_points"],  # 合計金額
        
        # オプション詳細
        options=options,
        
        status=reservation["status"],
        cast_label=reservation["cast_label"],    # 追加: cast_label
        description=reservation["description"],   # 追加: description
        color_code=reservation["color_code"],     # 追加: color_code
        reservation_note=reservation["reservation_note"],
        cancel_reason=reservation["cancel_reason"]
    )
    
    return response
