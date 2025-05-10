from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from ..services.cast_service import fetch_casts_for_tenant
from ..schemas.cast import CastOut
from typing import List

router = APIRouter()

@router.post("/casts", response_model=List[CastOut])
def get_casts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    tenant_id = current_user.id
    return fetch_casts_for_tenant(db, tenant_id)
