# Cast Profile Endpoints
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user # ユーザー情報取得
from app.db.models.user import User # Userモデルをインポート (型ヒント用)
from ..schema import prof_schema # スキーマをインポート
from ..service import prof_service # サービスをインポート

# 自身のAPIRouterインスタンスを定義
router = APIRouter()

@router.post("/get", response_model=prof_schema.CastProfRead)
def get_cast_profile_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 認証されたユーザーを取得
):
    """認証されたキャスト自身のプロフィールを取得 (POST)"""
    # current_user.id はキャストのユーザーID (ログイン時に取得)
    # ここでは user.id が cast_common_prof の cast_id に対応すると仮定
    # もし user テーブルと cast_common_prof テーブルの紐付け方が違う場合は修正が必要
    # current_user u304cu6587u5b57u5217u306eu5834u5408u3068u30aau30d6u30b8u30a7u30afu30c8u306eu5834u5408u306eu4e21u65b9u306bu5bfeu5fdc
    cast_id = current_user if isinstance(current_user, (int, str)) else current_user.id
    
    # u6587u5b57u5217u306eu5834u5408u306fu6574u6570u306bu5909u63db
    if isinstance(cast_id, str) and cast_id.isdigit():
        cast_id = int(cast_id)
    return prof_service.get_profile_service(db, cast_id)

@router.post("/update", response_model=prof_schema.CastProfRead)
def update_cast_profile_endpoint(
    prof_data: prof_schema.CastProfUpdate, # リクエストボディで更新データを受け取る
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """認証されたキャスト自身のプロフィールを更新 (POST)"""
    # current_user u304cu6587u5b57u5217u306eu5834u5408u3068u30aau30d6u30b8u30a7u30afu30c8u306eu5834u5408u306eu4e21u65b9u306bu5bfeu5fdc
    cast_id = current_user if isinstance(current_user, (int, str)) else current_user.id
    
    # u6587u5b57u5217u306eu5834u5408u306fu6574u6570u306bu5909u63db
    if isinstance(cast_id, str) and cast_id.isdigit():
        cast_id = int(cast_id)
    return prof_service.update_profile_service(db, cast_id, prof_data)
