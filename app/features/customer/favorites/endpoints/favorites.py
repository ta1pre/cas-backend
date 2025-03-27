# app/features/customer/favorites/endpoints/favorites.py

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.features.customer.favorites.service.favorites_service import add_favorite, remove_favorite, get_favorites
from app.features.customer.favorites.schemas.favorites_schema import FavoriteResponse, FavoriteList

router = APIRouter()

class UserIdRequest(BaseModel):
    user_id: int

@router.post("/get_favorites", response_model=FavoriteList)
def list_favorites(request: UserIdRequest, db: Session = Depends(get_db)):
    """ユーザーのお気に入り一覧を取得"""
    return get_favorites(request.user_id, db)

@router.post("/{cast_id}")
def add_to_favorites(cast_id: int, request: UserIdRequest, db: Session = Depends(get_db)):
    """お気に入りに追加"""
    return add_favorite(request.user_id, cast_id, db)

@router.delete("/{cast_id}")
def remove_from_favorites(cast_id: int, request: UserIdRequest, db: Session = Depends(get_db)):
    """お気に入りから削除"""
    return remove_favorite(request.user_id, cast_id, db)
