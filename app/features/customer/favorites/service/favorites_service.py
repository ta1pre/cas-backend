# app/features/customer/favorites/service/favorites_service.py

from sqlalchemy.orm import Session, aliased
from sqlalchemy.future import select
from fastapi import HTTPException
from app.db.models.cast_favorites import CastFavorite
from app.db.models.cast_common_prof import CastCommonProf
from app.db.models.media_files import MediaFile
from app.features.customer.favorites.schemas.favorites_schema import FavoriteList, FavoriteResponse, CastInfo
from app.features.customer.castprof.repositories.image_repository import get_cast_images

def get_favorites(user_id: int, db: Session) -> FavoriteList:
    """ユーザーのお気に入り一覧を取得"""
    # MediaFileテーブルへのアリースを定義
    MediaAlias = aliased(MediaFile)
    
    # お気に入りリストを取得
    favorites = db.query(CastFavorite).filter(CastFavorite.user_id == user_id).all()
    
    # お気に入りレスポンスリストを作成
    favorite_responses = []
    
    for favorite in favorites:
        # お気に入りの基本情報を取得
        favorite_response = FavoriteResponse.from_orm(favorite)
        
        # キャスト情報を取得
        cast = db.query(CastCommonProf).filter(CastCommonProf.cast_id == favorite.cast_id).first()
        
        if cast:
            # プロフィール画像を取得
            profile_image_query = (
                select(MediaAlias.file_url)
                .where(
                    (MediaAlias.target_id == cast.cast_id) &
                    (MediaAlias.target_type == "profile_common") &
                    (MediaAlias.order_index == 0)
                )
            )
            profile_image_result = db.execute(profile_image_query).first()
            profile_image_url = profile_image_result[0] if profile_image_result else None
            
            # キャストの画像を取得
            images = get_cast_images(cast.cast_id, db)
            
            # キャスト情報を設定
            cast_info = CastInfo(
                name=cast.name,
                profile_image_url=profile_image_url,
                age=cast.age,
                images=images
            )
            
            # お気に入りレスポンスにキャスト情報を追加
            favorite_response.cast_info = cast_info
        
        favorite_responses.append(favorite_response)
    
    return FavoriteList(favorites=favorite_responses)

def add_favorite(user_id: int, cast_id: int, db: Session):
    """お気に入りに追加"""
    try:
        favorite = CastFavorite(user_id=user_id, cast_id=cast_id)
        db.add(favorite)
        db.commit()
        db.refresh(favorite)
        return {"message": "お気に入りに追加しました"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="お気に入りの追加に失敗しました")

def remove_favorite(user_id: int, cast_id: int, db: Session):
    """お気に入りから削除"""
    favorite = db.query(CastFavorite).filter(
        CastFavorite.user_id == user_id,
        CastFavorite.cast_id == cast_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="お気に入りが見つかりません")
    
    try:
        db.delete(favorite)
        db.commit()
        return {"message": "お気に入りから削除しました"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="お気に入りの削除に失敗しました")
