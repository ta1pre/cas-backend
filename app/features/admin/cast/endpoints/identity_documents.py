"""Admin Cast: 身分証画像取得エンドポイント"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.media_files import MediaFile
from app.features.admin.cast.schemas.identity_document import IdentityDocOut
from app.core.security import get_current_user  # ✅ 要: 管理者ユーザー認証

router = APIRouter()


@router.get("/{cast_id}/identity-documents", response_model=List[IdentityDocOut])
async def list_identity_documents(
    cast_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """指定キャストの身分証画像を取得

    - target_type は `cast_identity_verification` 固定
    - アップロード日時の降順で返す
    """
    records: List[MediaFile] = (
        db.query(MediaFile)
        .filter(
            MediaFile.target_type == "cast_identity_verification",
            MediaFile.target_id == cast_id,
        )
        .order_by(MediaFile.created_at.desc())
        .all()
    )

    if records is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No documents found",
        )

    # file_url → url へマッピング
    return [
        IdentityDocOut(
            id=doc.id,
            url=doc.file_url,
            created_at=doc.created_at,
            status=None,  # 余地
        )
        for doc in records
    ]
