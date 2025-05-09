from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.db.models.user import User
from app.db.models.user_invite_tracking import UserInviteTracking
from app.features.referral.schemas.invitee import Invitee
from typing import List

router = APIRouter()

@router.get("/invitees", response_model=List[Invitee], summary="自分が紹介したユーザー一覧を取得")
def get_invitees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invitees = db.query(UserInviteTracking).filter(UserInviteTracking.inviter_user_id == current_user.id).all()
    result = [
        Invitee(
            display_number=invitee.display_number,
            total_earned_point=invitee.total_earned_point,
            created_at=invitee.created_at.strftime("%Y-%m-%d") if invitee.created_at else None
        )
        for invitee in invitees
    ]
    return result
