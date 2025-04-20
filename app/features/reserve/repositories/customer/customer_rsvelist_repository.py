# app/features/reserve/repositories/customer/customer_rsvelist_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.models.resv_reservation import ResvReservation
from app.db.models.cast_common_prof import CastCommonProf
from app.db.models.point_details import PointDetailsCourse
from app.db.models.resv_reservation_option import ResvReservationOption
from app.db.models.point_details import PointDetailsOption
from app.db.models.resv_status_detail import ResvStatusDetail
from app.db.models.resv_chat import ResvChat
from app.db.models.station import Station

def get_customer_reservations(db: Session, user_id: int, limit: int, offset: int):
    """
    ここで引数の順番を (db, user_id, limit, offset) にする
    """
    latest_message_subquery = (
        select(
            ResvChat.reservation_id,
            func.max(ResvChat.created_at).label("last_message_time"),
            func.substr(ResvChat.message, 1, 5).label("last_message_preview")
        )
        .group_by(ResvChat.reservation_id)
        .subquery()
    )

    stmt = (
        select(
            ResvReservation.id.label("reservation_id"),
            ResvReservation.cast_id,
            CastCommonProf.name.label("cast_name"),
            ResvStatusDetail.user_label.label("status"),
            ResvStatusDetail.status_key.label("status_key"),
            ResvReservation.start_time,
            PointDetailsCourse.course_name,
            func.coalesce(ResvReservation.course_points, 0).label("course_points"),  # NULLでも0で返す
            PointDetailsCourse.cost_points.label("course_price"),
            ResvReservation.reservation_fee.label("reservation_fee"),  # resv_reservationテーブルから取得
            ResvReservation.traffic_fee,
            func.coalesce(func.sum(ResvReservationOption.option_price), 0).label("total_option_price"),
            func.coalesce(func.group_concat(func.distinct(PointDetailsOption.option_name), ','), '').label("option_list"),
            func.coalesce(func.group_concat(func.distinct(ResvReservationOption.option_price), ','), '').label("option_price_list"),
            ResvStatusDetail.color_code,
            Station.name.label("location"),
            latest_message_subquery.c.last_message_time,
            latest_message_subquery.c.last_message_preview
        )
        .join(CastCommonProf, ResvReservation.cast_id == CastCommonProf.cast_id)
        .join(PointDetailsCourse, ResvReservation.course_id == PointDetailsCourse.id)
        .join(ResvStatusDetail, ResvReservation.status == ResvStatusDetail.status_key)
        .join(Station, ResvReservation.location == Station.id)
        .outerjoin(ResvReservationOption, ResvReservation.id == ResvReservationOption.reservation_id)
        .outerjoin(PointDetailsOption, ResvReservationOption.option_id == PointDetailsOption.id)
        .outerjoin(latest_message_subquery, ResvReservation.id == latest_message_subquery.c.reservation_id)
        .filter(ResvReservation.user_id == user_id)
        .group_by(ResvReservation.id)
        .order_by(ResvReservation.start_time.desc())
        .limit(limit)
        .offset(offset)
    )

    results = db.execute(stmt).mappings().all()  # 「.mappings().all()」でOK
    print("【DEBUG】customer_rsvelist_repository results sample:", results[:1])
    return results

def get_total_reservation_count(db: Session, user_id: int):
    return db.query(ResvReservation).filter(ResvReservation.user_id == user_id).count()
