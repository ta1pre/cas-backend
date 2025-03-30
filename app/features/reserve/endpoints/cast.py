# app/features/reserve/endpoints/cast.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.features.reserve.schemas.cast.cast_station_schema import (
    StationSuggestRequest,
    StationSuggestResponse,
    StationUpdateRequest,
    StationUpdateResponse
)
from app.features.reserve.service.cast.cast_station_service import suggest_stations, update_station
from typing import List

from app.features.reserve.schemas.cast.cast_course_schema import CastCourseListResponse
from app.features.reserve.service.cast.cast_course_service import get_cast_courses, get_all_courses, get_filtered_courses


cast_router = APIRouter()

@cast_router.post("/station/suggest", response_model=List[StationSuggestResponse])
def get_suggested_stations(request: StationSuggestRequest, db: Session = Depends(get_db)):
    """駅名のサジェスト検索"""
    return suggest_stations(db, request.query)

@cast_router.post("/station/update", response_model=StationUpdateResponse)
def update_station_info(request: StationUpdateRequest, db: Session = Depends(get_db)):
    """予約の駅情報を更新"""
    success = update_station(db, request.reservation_id, request.cast_id, request.station_id)
    return StationUpdateResponse(
        success=success,
        message="駅情報の更新に成功しました" if success else "駅情報の更新に失敗しました"
    )

@cast_router.post("/test")
def test_cast():
    return {"message": "Cast endpoint is working"}

# ✅ キャスト用予約一覧取得API（ページネーション対応）
from app.features.reserve.service.cast.cast_rsvelist_service import get_cast_reservation_list
from app.features.reserve.schemas.cast.cast_rsvelist_schema import CastRsveListResponse

@cast_router.post("/rsvelist", response_model=CastRsveListResponse)
def cast_reservation_list(request: dict, db: Session = Depends(get_db)):
    cast_id = request.get("cast_id")
    page = request.get("page", 1)
    limit = request.get("limit", 10)

    if not cast_id:
        raise HTTPException(status_code=400, detail="cast_id は必須です")

    response_obj = get_cast_reservation_list(db, cast_id, page, limit)
    return response_obj


# ✅ 個別予約ページ
from app.features.reserve.service.cast.cast_detail_service import get_reservation_detail
from app.features.reserve.schemas.cast.cast_detail_schema import CastReservationDetailResponse
@cast_router.post("/detail", response_model=CastReservationDetailResponse)
def fetch_reservation_detail(request: dict, db: Session = Depends(get_db)):
    reservation_id = request.get("reservation_id")
    cast_id = request.get("cast_id")

    if not reservation_id or not cast_id:
        raise HTTPException(status_code=400, detail="reservation_id, cast_id は必須です")

    # 予約詳細を取得
    response = get_reservation_detail(db, reservation_id, cast_id)
    
    # デバッグ用: レスポンスの内容をログに出力
    print(f"DEBUG - 予約詳細レスポンス: {response.dict()}")
    print(f"DEBUG - オプション情報: {response.options}")
    print(f"DEBUG - オプション料金合計: {response.options_fee}")
    
    # 指名料、オプション料金、交通費、合計金額の詳細をログに出力
    print(f"DEBUG - 料金詳細:")
    print(f"  - 指名料: {response.designation_fee}")
    print(f"  - オプション料金: {response.options_fee}")
    print(f"  - 交通費: {response.traffic_fee}")
    print(f"  - 予約基本料金: {response.reservation_fee}")
    print(f"  - 合計金額: {response.total_points}")
    
    return response


# ✅ 表示用オプションの取得
# スキーマ & サービスインポート
from app.features.reserve.schemas.cast.cast_options_schema import (
    CastOptionRequest,
    CastOptionResponse
)
from app.features.reserve.service.cast.cast_options_service import get_cast_options

@cast_router.post("/options", response_model=CastOptionResponse)
def fetch_cast_options(request: CastOptionRequest, db: Session = Depends(get_db)):
    """
    キャストが対応できるオプション一覧 & 予約に紐づいているオプション一覧を取得
    """
    return get_cast_options(db, request)


# ✅ 予約情報編集API
from app.features.reserve.schemas.cast.cast_edit_schema import (
    CastReservationEditRequest,
    CastReservationEditResponse
)
from app.features.reserve.service.cast.cast_edit_service import edit_reservation

@cast_router.post("/edit", response_model=CastReservationEditResponse)
def edit_reservation_endpoint(request: CastReservationEditRequest, db: Session = Depends(get_db)):
    """
    キャストによる予約情報一括編集API
    更新と同時にステータス履歴を追加し、オプションを入れ替える
    """
    # リクエストデータをデバッグ出力
    print(f"DEBUG - [編集API] リクエストデータ: {request}")
    print(f"DEBUG - [編集API] 予約ID: {request.reservation_id}")
    print(f"DEBUG - [編集API] キャストID: {request.cast_id}")
    print(f"DEBUG - [編集API] 選択オプション: {request.option_ids}")
    print(f"DEBUG - [編集API] カスタムオプション: {request.custom_options}")
    print(f"DEBUG - [編集API] 交通費: {request.transportation_fee}")
    
    # カスタムオプションの詳細をログ出力
    for i, opt in enumerate(request.custom_options):
        print(f"DEBUG - [編集API] カスタムオプション #{i+1}: 名前={opt.name}, 価格={opt.price}")
    
    # 予約編集処理を実行
    response = edit_reservation(db, request)
    return response


# ✅ コース一覧取得API
@cast_router.post("/courses", response_model=CastCourseListResponse)
def fetch_cast_courses(request: dict, db: Session = Depends(get_db)):
    """
    キャストのコース一覧を取得するエンドポイント
    """
    cast_id = request.get("cast_id")
    return get_cast_courses(db, cast_id)

@cast_router.post("/all-courses", response_model=CastCourseListResponse)
def fetch_all_courses(db: Session = Depends(get_db)):
    """
    全てのアクティブなコースを取得するエンドポイント
    """
    return get_all_courses(db)

@cast_router.post("/filtered-courses", response_model=CastCourseListResponse)
def fetch_filtered_courses(request: dict = None, db: Session = Depends(get_db)):
    """
    キャストのフィルタリング条件に基づいてコースの一覧を取得するエンドポイント
    
    requestにキャストIDが含まれる場合、キャストのフィルタリング条件に基づいてコースの一覧を取得する
    """
    cast_id = None
    if request:
        cast_id = request.get("cast_id")
    return get_filtered_courses(db, cast_id)
