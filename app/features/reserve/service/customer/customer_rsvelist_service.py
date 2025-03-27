from sqlalchemy.orm import Session
from app.features.reserve.repositories.customer.customer_rsvelist_repository import get_customer_reservations, get_total_reservation_count
from app.features.reserve.schemas.customer.customer_rsvelist_schema import (
    CustomerRsveListItemResponse,
    CustomerRsveListResponse,
)

def format_reservation_data(reservation):
    return {
        "reservation_id": reservation.reservation_id,
        "cast_id": reservation.cast_id,
        "cast_name": reservation.cast_name,
        "status": reservation.status,
        "status_key": reservation.status_key,
        "start_time": reservation.start_time,
        "course_name": reservation.course_name,
        "location": reservation.location,  # ✅ ここを追加
        "course_price": reservation.course_price,
        "reservation_fee": reservation.reservation_fee,
        "traffic_fee": reservation.traffic_fee,
        "option_list": [opt.strip() for opt in reservation.option_list.split(",") if opt.strip()],
        "option_price_list": [int(price) for price in reservation.option_price_list.split(",") if price.isdigit()],
        "total_option_price": reservation.total_option_price or 0,
        "total_price": None,
        "color_code": reservation.color_code,
        "last_message_time": reservation.last_message_time if hasattr(reservation, 'last_message_time') else None,
        "last_message_preview": reservation.last_message_preview if hasattr(reservation, 'last_message_preview') else None
    }


# customer_rsvelist_service.py
def get_customer_reservation_list(db: Session, user_id: int, page: int, limit: int) -> CustomerRsveListResponse:
    offset = (page - 1) * limit
    reservations = get_customer_reservations(db, user_id, limit, offset)
    total_count = get_total_reservation_count(db, user_id)

    formatted_reservations = [format_reservation_data(res) for res in reservations]

    return CustomerRsveListResponse(
        page=page,
        limit=limit,
        total_count=total_count,
        reservations=formatted_reservations
    )