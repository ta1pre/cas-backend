# app/features/reserve/endpoints/customer.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.features.reserve.schemas.customer.offer_schema import OfferReservationResponse
from app.features.reserve.service.customer.offer_service import create_reservation
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.features.reserve.service.customer.customer_cast_service import get_customer_cast_info
from app.features.reserve.schemas.customer.customer_cast_schema import CustomerCastRequest, CustomerCastResponse
from app.features.reserve.schemas.customer.customer_station_schema import CustomerStationRequest, CustomerStationResponse
from app.features.reserve.service.customer.customer_station_service import get_stations
from app.features.reserve.schemas.customer.customer_course_schema import CustomerCourseResponse
from app.features.reserve.service.customer.customer_course_service import get_available_courses_by_cast_id
from app.features.reserve.schemas.customer.offer_schema import OfferReservationCreate, OfferReservationResponse
from app.features.reserve.schemas.customer.customer_rsvelist_schema import CustomerRsveListResponse
from app.features.reserve.service.customer.customer_rsvelist_service import get_customer_reservation_list


customer_router = APIRouter()

@customer_router.post("/offer", response_model=OfferReservationResponse)
def offer_reservation(data: OfferReservationCreate, db: Session = Depends(get_db)):
    print("📡 受け取ったデータ:", data.dict())  # ✅ model_dump() を dict() に変更
    return create_reservation(db, data)


@customer_router.post("/cast", response_model=CustomerCastResponse)
def get_cast_for_customer(request: CustomerCastRequest, db: Session = Depends(get_db)):
    """カスタマー用のキャスト情報取得API"""
    cast = get_customer_cast_info(request.cast_id, db)
    if not cast:
        raise HTTPException(status_code=404, detail="キャストが見つかりません")
    return cast

@customer_router.post("/get_station", response_model=CustomerStationResponse)
def get_station(request: CustomerStationRequest, db: Session = Depends(get_db)):
    """ユーザーとキャストの登録駅を取得"""
    if not request.user_id or not request.cast_id:
        raise HTTPException(status_code=400, detail="user_id と cast_id は必須です")
    
    stations = get_stations(request.user_id, request.cast_id, db)
    return stations

@customer_router.post("/get_courses", response_model=list[CustomerCourseResponse])
def get_courses(request: dict, db: Session = Depends(get_db)):
    cast_id = request.get("cast_id")
    if not cast_id:
        raise HTTPException(400, "cast_id は必須です")

    courses = get_available_courses_by_cast_id(cast_id, db)
    if not courses:
        raise HTTPException(status_code=404, detail="該当するコースがありません")

    print("✅ APIレスポンス:", courses)  # ✅ デバッグ用のログ追加
    return courses

# ✅ 予約一覧取得API（ページネーション対応）
@customer_router.post("/rsvelist", response_model=CustomerRsveListResponse)
def get_reservation_list(request: dict, db: Session = Depends(get_db)):
    user_id = request.get("user_id")
    page = request.get("page", 1)
    limit = request.get("limit", 10)

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id は必須です")

    response_obj = get_customer_reservation_list(db, user_id, page, limit)
    return response_obj  # ← これを1つのオブジェクトとして返す
    