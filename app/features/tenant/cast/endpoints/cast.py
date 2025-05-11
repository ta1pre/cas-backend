from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from ..services.cast_service import fetch_casts_for_tenant, register_cast, update_cast_profile
from ..schemas.cast import CastOut, CastCreate
from typing import List, Optional
import logging
from app.db.models.cast_common_prof import CastCommonProf

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/casts", response_model=List[CastOut])
def get_casts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    tenant_id = current_user.id
    return fetch_casts_for_tenant(db, tenant_id)

@router.post("/create")
def save_cast(
    cast_id: Optional[int] = Body(None),
    cast: CastCreate = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        if cast_id:
            return update_cast_profile(db, cast_id, cast, current_user.id)
        return register_cast(db, cast, current_user.id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error(f"キャスト保存エラー: {str(e)}")
        raise HTTPException(400, str(e))
