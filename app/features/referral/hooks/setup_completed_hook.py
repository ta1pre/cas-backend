from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.models.user_invite_tracking import UserInviteTracking
import logging

logger = logging.getLogger(__name__)

def on_setup_completed(user_id: int, db: Session):
    """
    セットアップ完了時の処理
    
    Args:
        user_id: ユーザーID
        db: データベースセッション
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"ユーザーが見つかりません - UserID: {user_id}")
        return
    
    logger.info(f"セットアップ完了 - UserID: {user_id}, TrackingID: {user.tracking_id}")
    
    # inviter_user_id を tracking_id から検索
    inviter = db.query(User).filter(User.invitation_id == user.tracking_id).first()
    if inviter:
        inviter_user_id = inviter.id
        logger.info(f"招待者特定成功 - inviter_user_id: {inviter_user_id}, tracking_id: {user.tracking_id}")
    else:
        inviter_user_id = None
        logger.warning(f"招待者が見つかりません - tracking_id: {user.tracking_id}")

    # inviter_user_idが見つかった場合のみ登録（なければスキップも可）
    if inviter_user_id:
        # inviter_user_idごとの既存件数をカウント
        display_number = db.query(UserInviteTracking).filter(
            UserInviteTracking.inviter_user_id == inviter_user_id
        ).count()
        logger.info(f"display_numberを自動採番: {display_number} (inviter_user_id={inviter_user_id})")

        tracking = UserInviteTracking(
            invited_user_id=user_id,
            inviter_user_id=inviter_user_id,
            display_number=display_number,
            total_earned_point=0
        )
        db.add(tracking)
        db.commit()
        logger.info(f"招待トラッキングレコード作成 - ID: {tracking.id}, 招待ユーザーID: {user_id}, display_number: {display_number}")
    else:
        logger.warning(f"user_invite_trackingsへの登録をスキップ - 招待者不明 (tracking_id: {user.tracking_id})")
