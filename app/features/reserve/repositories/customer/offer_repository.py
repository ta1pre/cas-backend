from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db.models.resv_reservation import ResvReservation
from app.features.reserve.schemas.customer.offer_schema import OfferReservationCreate
from app.db.models.point_details import PointDetailsCourse  # コースモデルをimport
from app.db.models.cast_common_prof import CastCommonProf  # キャストモデルをimport
from app.features.reserve.repositories.common.price_calculator import calculate_reservation_points  # 共通料金計算モジュールをimport

# JST (UTC+9) のタイムゾーンオブジェクト
JST = timezone(timedelta(hours=9))

def save_reservation(db: Session, data: OfferReservationCreate, start_time: datetime) -> ResvReservation:
    print("📡 save_reservation: 開始")  # デバッグログ

    # `start_time` を JST に統一
    if start_time.tzinfo is None or start_time.tzinfo.utcoffset(start_time) is None:
        start_time = start_time.replace(tzinfo=timezone.utc).astimezone(JST)
    else:
        start_time = start_time.astimezone(JST)

    # コース名とコースタイプからコースを取得
    course = db.query(PointDetailsCourse).filter(
        PointDetailsCourse.course_name == data.courseName,
        PointDetailsCourse.course_type == data.courseType
    ).first()
    
    if not course:
        # コースが見つからない場合はエラー
        raise ValueError(f"courseName={data.courseName}, courseType={data.courseType} に該当するコースがありません。")
    
    course_id = course.id  # 正しいcourse_idを設定

    # 合計ポイントの計算
    option_points = 0  # 現状は 0 に固定
    traffic_fee = 0  # 交通費は現状 0 に固定
    
    # 共通関数を使って料金計算
    points_data = calculate_reservation_points(
        db, 
        course_id, 
        data.castId, 
        option_points, 
        traffic_fee
    )

    print(f"📡 予約データ準備完了: course_id={course_id}, course_name={data.courseName}, course_type={points_data['course_type']}, duration={points_data['duration_minutes']}分")
    print(f"📡 料金情報: fee_type={points_data['fee_type']}, base_fee={points_data['base_fee']}, reservation_fee={points_data['reservation_fee']}")
    print(f"📡 ポイント計算: course_base_points={points_data['course_base_points']}, course_points={points_data['course_points']}, total_points={points_data['total_points']}")
    print(f"📡 キャスト報酬: cast_reward_points={points_data['cast_reward_points']} (reservation_fee={points_data['reservation_fee']} + option_points={option_points} + traffic_fee={traffic_fee})")
    print(f"📡 予約情報: start_time={start_time}")  # 確認用ログ

    # 予約データの作成
    reservation = ResvReservation(
        user_id=data.userId,
        cast_id=data.castId,
        course_id=course_id,  # 正しいcourse_idを設定
        course_points=points_data['course_points'],  # コースポイント（基本ポイント + reservation_fee）
        option_points=option_points,
        reservation_fee=points_data['reservation_fee'],  # 正しく計算されたreservation_fee
        total_points=points_data['total_points'],  # 合計ポイント
        cast_reward_points=points_data['cast_reward_points'],
        start_time=start_time,  # JSTに統一
        end_time=start_time + points_data['end_time_delta'],  # コース時間に応じた終了時間
        location=data.station,
        latitude=data.latitude if data.latitude else 0.0,
        longitude=data.longitude if data.longitude else 0.0,
        status="requested",
        cancel_reason=None,
        is_reminder_sent=False,
        # created_at, updated_at は **削除**（DBに任せる）
    )

    print("📡 予約データをDBに追加")  # DBに追加する直前

    # DBに保存
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    print("✅ 予約データ保存完了")  # ここまで来ているか確認
    return reservation
