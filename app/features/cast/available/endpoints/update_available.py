from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.session import get_db
from app.db.models.cast_common_prof import CastCommonProf
from datetime import datetime, timedelta, timezone

router = APIRouter()

@router.post("/")
async def update_available_at(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    ログイン中キャストのavailable_atを現在時刻に更新
    """
    # current_user (cast_id) でキャスト自身を特定
    cast = db.query(CastCommonProf).filter(CastCommonProf.cast_id == current_user).first()
    if not cast:
        return {"message": "Cast not found"}
    # 日本時間(JST)で現在時刻をセット
    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst)
    # 60分以内ならエラー返却
    if cast.available_at:
        # DBのavailable_atもJSTとして扱う
        if cast.available_at.tzinfo is None:
            available_at_jst = cast.available_at.replace(tzinfo=jst)
        else:
            available_at_jst = cast.available_at.astimezone(jst)
        diff = (now_jst - available_at_jst).total_seconds() / 60
        if diff < 60:
            return {"message": "受付開始は前回から60分経過後に可能です"}
    cast.available_at = now_jst
    db.commit()
    db.refresh(cast)
    return {"message": "Available time updated successfully"}
