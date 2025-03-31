# app/features/setup/endpoints/setup_status.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.features.setup.schemas.status_schema import ProfileUpdateRequest
from app.features.setup.repositories.setup_status_repository import SetupStatusRepository
from app.features.setup.services.status_service import delete_cast_profile, delete_user_media_files, update_user_setup_status 
from app.db.models.user import User
from app.db.models.cast_common_prof import CastCommonProf
from app.db.models.cast_rank import CastRank
from sqlalchemy.exc import IntegrityError
from typing import Any, Dict

router = APIRouter()

@router.post("/update")
def update_profile(request: ProfileUpdateRequest, db: Session = Depends(get_db)):
    setup_repo = SetupStatusRepository(db)
    print("Received Request:", request.dict())

    # ユーザーが存在するか確認
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # user_type を更新
    user.user_type = request.user_type
    user.sex = "female" if request.user_type == "cast" else "male"
    
    # キャストタイプを設定（新規追加）
    if request.user_type == "cast" and request.cast_type:
        user.cast_type = request.cast_type
    
    db.commit()

    # ✅ customer の場合、nick_name を更新し、CastCommonProf + 画像を削除
    if request.user_type == "customer":
        user.nick_name = request.profile_data.get("nickname")
        db.commit()

        # ✅ CastCommonProf を削除
        delete_cast_profile(request.user_id, db)

        # ✅ キャストのメディアファイル（S3 + DB）を削除
        delete_user_media_files(request.user_id, db)
        
        # ✅ ステータスをcompletedに。
        update_user_setup_status(request.user_id, db)

        return {
            "message": "プロフィールが更新されました",
            "user_type": user.user_type,
            "sex": user.sex,
            "nickname": user.nick_name
        }

    # ✅ rank_id=1 のデフォルトエントリーがあるか確認（無ければ作成）
    rank = db.query(CastRank).filter(CastRank.id == 1).first()
    if not rank:
        new_rank = CastRank(id=1, rank_name="Default Rank", base_fee=0, description="デフォルトランク")
        db.add(new_rank)
        db.commit()

    # cast の場合、cast_common_prof を確認
    cast_profile = db.query(CastCommonProf).filter(CastCommonProf.cast_id == request.user_id).first()
    if cast_profile:
        # 既存データを更新
        cast_profile.name = request.profile_data.get("cast_name")
        cast_profile.age = request.profile_data.get("age")
        cast_profile.height = request.profile_data.get("height")
        # キャストタイプを設定（新規追加）
        if request.cast_type:
            cast_profile.cast_type = 'A' if request.cast_type == 'cas' else 'B'
    else:
        # 新規作成 (rank_id を 1 に設定)
        try:
            cast_profile = CastCommonProf(
                cast_id=request.user_id,
                cast_type='A' if not request.cast_type or request.cast_type == 'cas' else 'B',
                rank_id=1,
                name=request.profile_data.get("cast_name"),
                age=request.profile_data.get("age"),
                height=request.profile_data.get("height")
            )
            db.add(cast_profile)
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Invalid foreign key reference to cast_rank: {str(e)}")

    db.commit()
    # ✅ setup_status を `completed` に更新
    update_user_setup_status(request.user_id, db)

    return {
        "message": "プロフィールが更新されました",
        "user_type": user.user_type,
        "sex": user.sex,
        "cast_name": cast_profile.name,
        "age": cast_profile.age,
        "height": cast_profile.height,
        "rank_id": cast_profile.rank_id,
        "cast_type": cast_profile.cast_type
    }

#ステータス確認
@router.get("/setup_status/{user_id}")
def get_setup_status(user_id: int, db: Session = Depends(get_db)):
    setup_repo = SetupStatusRepository(db)
    status = setup_repo.get_user_setup_status(user_id)
    
    if status == "not_found":
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"setup_status": status}




from pydantic import BaseModel  # ✅ `Pydantic` をインポート
# ✅ `user_id` を受け取るリクエストボディ（`BaseModel` を継承）
class TestRequest(BaseModel):
    user_id: int
@router.post("/test")
def test_api(request: TestRequest):
    return {"received_user_id": request.user_id}