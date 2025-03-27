from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.cast_common_prof import CastCommonProf
from app.core.security import get_current_user
from app.db.models.user import User

router = APIRouter()

@router.post("/register")
def register_cast(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):  
    """
    ✅ キャスト登録API
    - `user_id` を `get_current_user` から取得
    - `cast_common_prof` に `cast_id=user_id` の行を作成（既存の場合はスルー）
    """

    # 既に登録済みならスルー
    existing_cast = db.query(CastCommonProf).filter(CastCommonProf.cast_id == user_id).first()
    if existing_cast:
        return {"message": "既にキャスト登録されています"}

    # 新しいキャストを作成
    new_cast = CastCommonProf(cast_id=user_id)
    db.add(new_cast)
    db.commit()

    return {"message": "キャスト登録が完了しました"}
