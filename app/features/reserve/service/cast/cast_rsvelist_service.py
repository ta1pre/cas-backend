# 📂 app/features/reserve/services/cast_rsvelist_service.py

from sqlalchemy.orm import Session
from app.features.reserve.repositories.cast.cast_rsvelist_repository import (
    get_cast_reservations,
    get_total_reservation_count
)
from app.features.reserve.schemas.cast.cast_rsvelist_schema import CastRsveListResponse, CastRsveListItemResponse

def format_cast_reservation_data(reservation):
    return CastRsveListItemResponse(
        reservation_id=reservation.reservation_id,
        user_id=reservation.user_id,
        user_name=reservation.user_name,
        status=reservation.status,
        status_key=reservation.status_key,
        cast_label=reservation.status,       # Use status (cast_label) from ResvStatusDetail
        description=reservation.description, # Add description from ResvStatusDetail
        start_time=reservation.start_time,
        course_name=reservation.course_name,
        location=reservation.location,
        station_name=reservation.station_name,
        course_price=reservation.course_price,
        traffic_fee=reservation.traffic_fee,
        cast_reward_points=reservation.cast_reward_points,  # ✅ Add cast_reward_points
        color_code=reservation.color_code,
        last_message_time=reservation.last_message_time,
        last_message_preview=reservation.last_message_preview
    )

def get_cast_reservation_list(db: Session, cast_id: int, page: int, limit: int) -> CastRsveListResponse:
    offset = (page - 1) * limit
    reservations = get_cast_reservations(db, cast_id, limit, offset)
    total_count = get_total_reservation_count(db, cast_id)

    formatted_reservations = [format_cast_reservation_data(res) for res in reservations]

    return CastRsveListResponse(
        page=page,
        limit=limit,
        total_count=total_count,
        reservations=formatted_reservations
    )
