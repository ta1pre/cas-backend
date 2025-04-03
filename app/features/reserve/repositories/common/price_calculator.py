from datetime import timedelta
from sqlalchemy.orm import Session
from app.db.models.cast_common_prof import CastCommonProf
from app.db.models.point_details import PointDetailsCourse

def calculate_reservation_points(
    db: Session,
    course_id: int,
    cast_id: int,
    option_points: int = 0,
    traffic_fee: int = 0
):
    """
    予約ポイントを計算する共通関数
    
    Args:
        db: DBセッション
        course_id: コースID
        cast_id: キャストID
        option_points: オプションポイント（デフォルト0）
        traffic_fee: 交通費（デフォルト0）
        
    Returns:
        dict: 計算結果を含む辞書
        {
            'course_base_points': コース基本ポイント,
            'reservation_fee': 予約料金,
            'course_points': コースポイント,
            'cast_reward_points': キャスト報酬ポイント,
            'total_points': 合計ポイント,
            'duration_minutes': コース時間（分）
        }
    """
    # コース情報取得
    course = db.query(PointDetailsCourse).filter(PointDetailsCourse.id == course_id).first()
    if not course:
        raise ValueError(f"course_id={course_id} に該当するコースがありません。")
    
    course_base_points = course.cost_points
    duration_minutes = course.duration_minutes
    course_type = course.course_type
    
    # キャスト情報取得
    cast_prof = db.query(CastCommonProf).filter(CastCommonProf.cast_id == cast_id).first()
    if not cast_prof:
        raise ValueError(f"cast_id={cast_id} に該当するキャストがありません。")
    
    # コースタイプに応じた料金を選択
    if course_type == 1:
        base_fee = cast_prof.reservation_fee or 0
        fee_type = "reservation_fee"
    elif course_type == 2:
        base_fee = cast_prof.reservation_fee_deli or 0
        fee_type = "reservation_fee_deli"
    else:
        raise ValueError(f"不明なコースタイプ: {course_type}")
    
    # 予約料金の計算
    reservation_fee = (duration_minutes / 60) * base_fee
    
    # 各種ポイント計算
    course_points = course_base_points + reservation_fee
    cast_reward_points = reservation_fee + option_points + traffic_fee
    total_points = course_points + option_points + reservation_fee
    
    # 終了時間計算用
    end_time_delta = timedelta(minutes=duration_minutes)
    
    return {
        'course_base_points': course_base_points,
        'reservation_fee': reservation_fee,
        'course_points': course_points,
        'cast_reward_points': cast_reward_points,
        'total_points': total_points,
        'duration_minutes': duration_minutes,
        'end_time_delta': end_time_delta,
        'fee_type': fee_type,
        'base_fee': base_fee,
        'course_type': course_type,
        'course_name': course.course_name
    }
