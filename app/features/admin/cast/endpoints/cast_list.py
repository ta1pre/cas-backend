"""Admin Cast list endpoint"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing_extensions import Literal

from app.db.session import get_db
from app.features.admin.cast.repositories.cast_repository import CastRepository

router = APIRouter()

class CastItem(BaseModel):
    id: int
    nick_name: Optional[str] = None
    status: str
    thumbnail_url: Optional[str] = None  # サムネイル画像URL
    document_count: int = 0  # アップロード済み書類数

class CastListResponse(BaseModel):
    total: int
    items: List[CastItem]

@router.get("/list", response_model=CastListResponse)
def list_casts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: Literal["id", "nick_name", "status"] = Query("id"),
    sort_dir: Literal["asc", "desc"] = Query("asc"),
    db: Session = Depends(get_db)
):
    """キャスト一覧をページネーションして返す"""
    repo = CastRepository(db)
    total, items = repo.list_casts_with_status(page, page_size, sort_by, sort_dir)
    return {"total": total, "items": items}
