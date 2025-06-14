"""Admin Cast: Identity verification status update endpoint"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.features.admin.cast.schemas.identity_status_update import (
    CastIdentityStatusUpdateRequest,
    CastIdentityStatusUpdateResponse,
)
from app.features.admin.cast.repositories.cast_repository import CastRepository

router = APIRouter()


@router.api_route(
    "/{cast_id}/identity-verification/status",
    methods=["PUT", "POST"],
    response_model=CastIdentityStatusUpdateResponse,
    status_code=status.HTTP_200_OK,
)
async def update_identity_status(
    cast_id: int,
    body: CastIdentityStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """キャスト本人確認ステータスを更新する"""

    if body.status == "rejected" and not body.rejection_reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="rejection_reason is required when status is rejected",
        )

    repo = CastRepository(db)
    updated = repo.update_identity_verification_status(
        cast_id=cast_id,
        new_status=body.status,
        reviewer_id=current_user.id,
        rejection_reason=body.rejection_reason,
    )
    return {**updated, "message": "updated"}
