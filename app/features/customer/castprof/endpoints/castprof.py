#app/features/customer/castprof/endpoints/castprof.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.features.customer.castprof.service.castprof_service import fetch_cast_profile
from app.features.customer.castprof.schemas.castprof_schema import CastProfileRequest, CastProfileResponse

router = APIRouter()

@router.post("/", response_model=CastProfileResponse)
def get_profile(request: CastProfileRequest, db: Session = Depends(get_db)):
    """キャストのプロフィール情報を取得"""
    print(f"【バックエンド API 受信】 cast_id: {request.cast_id}, user_id: {request.user_id}")

    profile = fetch_cast_profile(request.cast_id, db)

    if not profile:
        raise HTTPException(status_code=404, detail="キャストが見つかりません")

    return profile
