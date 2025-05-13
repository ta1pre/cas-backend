from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.features.customer.search.service.search_service import fetch_cast_list
from app.features.customer.search.schemas.search_schema import SearchRequest  # スキーマをインポート
from app.features.customer.search.schemas.user_schema import UserPrefectureRequest  # スキーマをインポート
from app.features.customer.search.repositories.user_repository import get_user_prefecture, get_prefecture_name
from app.core.security import get_current_user
from app.db.models.user import User


router = APIRouter() 

@router.post("/user/prefecture")
def get_user_prefecture_endpoint(request: UserPrefectureRequest, db: Session = Depends(get_db)):
    """ユーザーの都道府県IDと名前を取得"""
    user_id = request.user_id
    prefecture_id = get_user_prefecture(db, user_id)
    print(f"【API DEBUG】user_id: {user_id}")
    print(f"【API DEBUG】取得した prefecture_id: {prefecture_id}")

    if prefecture_id is None:
        raise HTTPException(status_code=404, detail="User not found")

    prefecture_name = get_prefecture_name(db, prefecture_id=prefecture_id)

    return {
        "prefecture_id": prefecture_id,
        "prefecture_name": prefecture_name
    }


@router.post("/")
def search_casts(
    request: SearchRequest, 
    db: Session = Depends(get_db), 
    current_user_id: int = Depends(get_current_user)  # ここは `user_id` になっている
):
    print(f"【バックエンド API 受信】 offset: {request.offset}, limit: {request.limit}, sort: {request.sort}, filters: {request.filters}")

    filters = request.filters or {}

    # `current_user_id` を使って `user.prefecture` を取得
    user_prefecture = db.query(User.prefectures).filter(User.id == current_user_id.id if hasattr(current_user_id, 'id') else current_user_id).scalar()

    # フィルターに都道府県がない場合、ユーザーの都道府県をセット
    if "prefecture_id" not in filters or not filters["prefecture_id"]:
        if user_prefecture:
            filters["prefecture_id"] = user_prefecture
            print(f"【適用フィルター】 ユーザーの都道府県を適用: {filters['prefecture_id']}")

    return fetch_cast_list(request.limit, request.offset, request.sort, filters, db)
