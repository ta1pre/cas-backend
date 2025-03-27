from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db.models.resv_reservation import ResvReservation
from app.features.reserve.schemas.customer.offer_schema import OfferReservationCreate
from app.db.models.point_details import PointDetailsCourse  # ✅ コースモデルをimport
from app.db.models.cast_common_prof import CastCommonProf  # ✅ キャストモデルをimport

# ✅ JST (UTC+9) のタイムゾーンオブジェクト
JST = timezone(timedelta(hours=9))

def save_reservation(db: Session, data: OfferReservationCreate, start_time: datetime) -> ResvReservation:
    print("📡 save_reservation: 開始")  # ✅ デバッグログ

    # ✅ `start_time` を JST に統一
    if start_time.tzinfo is None or start_time.tzinfo.utcoffset(start_time) is None:
        start_time = start_time.replace(tzinfo=timezone.utc).astimezone(JST)
    else:
        start_time = start_time.astimezone(JST)

    # ✅ courseType に応じて course_id を設定
    if data.courseType == 1:
        course_id = 11
    elif data.courseType == 2:
        course_id = 13
    else:
        raise ValueError(f"無効な courseType={data.courseType} です。")

    # ✅ コース情報を取得（PointDetailsCourse）
    course = db.query(PointDetailsCourse).filter(PointDetailsCourse.id == course_id).first()
    if not course:
        raise ValueError(f"course_id={course_id} に該当するコースがありません。")
    
    course_points = course.cost_points  # ✅ コース料金
    cast_reward_points = course.cast_reward_points  # ✅ キャスト報酬ポイント

    # ✅ キャストの reservation_fee を取得（CastCommonProf）
    cast_prof = db.query(CastCommonProf).filter(CastCommonProf.cast_id == data.castId).first()
    reservation_fee = cast_prof.reservation_fee if cast_prof else 0  # ✅ 見つからない場合は 0 を設定

    # ✅ 合計ポイントの計算
    option_points = 0  # 現状は 0 に固定
    total_points = course_points + option_points + reservation_fee

    print(f"📡 予約データ準備完了: course_id={course_id}, course_points={course_points}, reservation_fee={reservation_fee}, total_points={total_points}, start_time={start_time}")  # ✅ 確認用ログ

    # ✅ 予約データの作成
    reservation = ResvReservation(
        user_id=data.userId,
        cast_id=data.castId,
        course_id=course_id,
        course_points=course_points,
        option_points=option_points,
        reservation_fee=reservation_fee,
        total_points=total_points,
        cast_reward_points=cast_reward_points,
        start_time=start_time,  # ✅ JSTに統一
        end_time=start_time + timedelta(minutes=90),
        location=data.station,
        latitude=data.latitude if data.latitude else 0.0,
        longitude=data.longitude if data.longitude else 0.0,
        status="requested",
        cancel_reason=None,
        is_reminder_sent=False,
        # ✅ created_at, updated_at は **削除**（DBに任せる）
    )

    print("📡 予約データをDBに追加")  # ✅ DBに追加する直前

    # ✅ DBに保存
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    print("✅ 予約データ保存完了")  # ✅ ここまで来ているか確認
    return reservation
