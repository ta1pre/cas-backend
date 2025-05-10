from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from ..services.cast_service import fetch_casts_for_tenant, register_cast
from ..schemas.cast import CastOut, CastCreate
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/casts", response_model=List[CastOut])
def get_casts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    tenant_id = current_user.id
    return fetch_casts_for_tenant(db, tenant_id)

@router.post("/create")
def create_cast(
    nick_name: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return register_cast(db, nick_name, current_user.id)
    except Exception as e:
        logger.error(f"キャスト登録エラー: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
