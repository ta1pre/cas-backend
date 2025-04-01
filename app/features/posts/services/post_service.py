from sqlalchemy.orm import Session
from typing import List, Optional
from app.features.posts.repositories import post_repository
from app.features.posts.schemas.post_schema import PostCreate, PostUpdate, PostResponse
from app.db.models.posts import Post


def create_post_service(db: Session, cast_id: int, post_data: PostCreate) -> Post:
    """
    新しい投稿を作成するサービス
    
    Args:
        db: データベースセッション
        cast_id: キャストID
        post_data: 投稿データ
    
    Returns:
        作成された投稿オブジェクト
    """
    # ここに必要なバリデーションロジックを追加できます
    # 例: 本文の長さチェック、NGワードフィルタリングなど
    
    return post_repository.create_post(
        db=db,
        cast_id=cast_id,
        body=post_data.body,
        photo_url=post_data.photo_url,
        status=post_data.status
    )


def get_post_service(db: Session, post_id: int) -> Optional[Post]:
    """
    IDで投稿を取得するサービス
    
    Args:
        db: データベースセッション
        post_id: 投稿ID
    
    Returns:
        投稿オブジェクトまたはNone
    """
    return post_repository.get_post_by_id(db=db, post_id=post_id)


def get_cast_posts_service(db: Session, cast_id: int, skip: int = 0, limit: int = 20) -> List[Post]:
    """
    キャストの投稿一覧を取得するサービス
    
    Args:
        db: データベースセッション
        cast_id: キャストID
        skip: スキップする件数
        limit: 取得件数上限
    
    Returns:
        投稿オブジェクトのリスト
    """
    return post_repository.get_posts_by_cast_id(db=db, cast_id=cast_id, skip=skip, limit=limit)


def update_post_service(db: Session, post_id: int, post_data: PostUpdate) -> Optional[Post]:
    """
    投稿を更新するサービス
    
    Args:
        db: データベースセッション
        post_id: 投稿ID
        post_data: 更新データ
    
    Returns:
        更新された投稿オブジェクトまたはNone
    """
    # ここに必要なバリデーションロジックを追加できます
    
    return post_repository.update_post(
        db=db,
        post_id=post_id,
        body=post_data.body,
        photo_url=post_data.photo_url,
        status=post_data.status
    )


def delete_post_service(db: Session, post_id: int) -> bool:
    """
    投稿を論理削除するサービス
    
    Args:
        db: データベースセッション
        post_id: 投稿ID
    
    Returns:
        削除成功ならTrue、失敗ならFalse
    """
    return post_repository.delete_post(db=db, post_id=post_id)


def like_post_service(db: Session, post_id: int) -> Optional[Post]:
    """
    投稿にいいねをするサービス
    
    Args:
        db: データベースセッション
        post_id: 投稿ID
    
    Returns:
        更新された投稿オブジェクトまたはNone
    """
    return post_repository.increment_likes(db=db, post_id=post_id)
