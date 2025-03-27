import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from app.db.session import get_db
from app.core.security import get_current_user

from app.features.cast.servicetype.repositories.servicetype_repository import ServiceTypeRepository
from app.features.cast.servicetype.schemas.servicetype_schema import ServiceTypeResponse, SelectedServiceTypeRequest, ServiceTypeRegisterRequest



logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/list", response_model=Dict[str, List[ServiceTypeResponse]])
def get_all_service_types(db: Session = Depends(get_db)):
    """
    ✅ サービスタイプ一覧を取得（is_active=1 のみ & カテゴリごとに整理）
    """
    service_repo = ServiceTypeRepository(db)
    service_types = service_repo.get_all_service_types()

    # ✅ `is_active=1` のデータのみ取得
    active_services = [service for service in service_types if service.is_active == 1]

    # ✅ カテゴリごとにデータを整理
    services_by_category = {}
    for service in active_services:
        category = service.category
        if category not in services_by_category:
            services_by_category[category] = []
        services_by_category[category].append({
            "id": service.id,
            "name": service.name,
            "weight": service.weight,
            "category": service.category,
            "is_active": service.is_active,
            "description": service.description if service.description is not None else ""  # ✅ None を空文字に変換！
        })

    return services_by_category

@router.post("/selected", response_model=List[int])
def get_selected_service_types(request: SelectedServiceTypeRequest, db: Session = Depends(get_db)):
    """
    ✅ キャストの選択したサービスタイプを取得
    """
    service_repo = ServiceTypeRepository(db)
    selected_services = service_repo.get_selected_service_types(request.cast_id)

    return selected_services  # ✅ 選択されているサービスタイプの ID のリストを返す

@router.post("/register")
def register_service_types(request: ServiceTypeRegisterRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    """
    ✅ キャストのサービスタイプを登録
    """
    service_repo = ServiceTypeRepository(db)
    service_repo.register_service_types(request.cast_id, request.service_type_ids)
    return {"message": "サービスタイプを登録しました"}

@router.post("/delete")
def delete_service_types(request: ServiceTypeRegisterRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    """
    ✅ キャストのサービスタイプを削除
    """
    service_repo = ServiceTypeRepository(db)
    service_repo.delete_service_types(request.cast_id, request.service_type_ids)
    return {"message": "サービスタイプを削除しました"}
