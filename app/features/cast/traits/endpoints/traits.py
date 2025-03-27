import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
from app.db.session import get_db
from app.features.cast.traits.repositories.traits_repository import TraitsRepository
from app.features.cast.traits.schemas.traits_schema import TraitResponse, SelectedTraitsRequest, TraitRegisterRequest
from app.core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/list", response_model=Dict[str, List[TraitResponse]])
def get_all_traits(db: Session = Depends(get_db)):
    """
    ✅ 特徴リストを取得（is_active=1 のみ取得 & カテゴリごとに整理）
    """
    traits_repo = TraitsRepository(db)
    traits = traits_repo.get_all_traits()

    active_traits = [trait for trait in traits if trait.is_active == 1]

    traits_by_category = {}
    for trait in active_traits:
        category = trait.category
        if category not in traits_by_category:
            traits_by_category[category] = []
        traits_by_category[category].append({
            "id": trait.id,
            "name": trait.name,
            "weight": trait.weight,
            "category": trait.category,
            "is_active": trait.is_active
        })

    return traits_by_category

@router.post("/selected", response_model=List[int])
def get_selected_traits(request: SelectedTraitsRequest, db: Session = Depends(get_db)):
    """
    ✅ 現在のキャストの選択状態を取得
    """
    traits_repo = TraitsRepository(db)
    selected_traits = traits_repo.get_selected_traits(request.cast_id)

    return selected_traits  # ✅ 選択されている特徴の ID のリストを返す

@router.post("/register")
def register_traits(request: TraitRegisterRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    """
    ✅ キャストの特徴を登録
    """
    traits_repo = TraitsRepository(db)
    traits_repo.register_traits(request.cast_id, request.trait_ids)
    return {"message": "特徴を登録しました"}

@router.post("/delete")
def delete_traits(request: TraitRegisterRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    """
    ✅ キャストの特徴を削除
    """
    traits_repo = TraitsRepository(db)
    traits_repo.delete_traits(request.cast_id, request.trait_ids)
    return {"message": "特徴を削除しました"}

@router.post("/hello")
def say_hello():
    """
    ✅ テスト用エンドポイント: 「こんにちわっと」を返す
    """
    return {"message": "こんにちわわわ"}

