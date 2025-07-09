from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.db.models.posts import Post
from app.db.models.user import User
from fastapi import HTTPException


def create_post(db: Session, cast_id: int, body: str, photo_url: Optional[str] = None, status: str = "public") -> Post:
    """
    新しい投稿を作成する
    
    Args:
        db: データベースセッション
        cast_id: キャストID
        body: 投稿本文
        photo_url: 画像のURL（任意）
        status: 公開ステータス（public/private/draft）
    
    Returns:
        作成された投稿オブジェクト
    """
    user = db.query(User).filter(User.id == cast_id).first()
    if not user:
        raise HTTPException(status_code=400, detail=f"Cast with id {cast_id} not found")
    db_post = Post(
        cast_id=cast_id,
        body=body,
        photo_url=photo_url,
        status=status
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_post_by_id(db: Session, post_id: int) -> Optional[Post]:
    """
    IDで投稿を取得する
    
    Args:
        db: データベースセッション
        post_id: 投稿ID
    
    Returns:
        投稿オブジェクトまたはNone
    """
    return db.query(Post).filter(Post.id == post_id, Post.deleted_at.is_(None)).first()


def get_public_posts_by_cast_id(db: Session, cast_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
    """
    キャストIDで公開投稿一覧を取得する
    
    Args:
        db: データベースセッション
        cast_id: キャストID
        skip: スキップする件数
        limit: 取得件数上限
    
    Returns:
        公開投稿オブジェクトのリスト
    """
    return db.query(Post)\
        .filter(Post.cast_id == cast_id, Post.deleted_at.is_(None), Post.status == "public")\
        .order_by(desc(Post.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_all_posts_by_cast_id(db: Session, cast_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
    """
    キャストIDで全ての投稿一覧を取得する（ステータス問わず）
    
    Args:
        db: データベースセッション
        cast_id: キャストID
        skip: スキップする件数
        limit: 取得件数上限
    
    Returns:
        全ての投稿オブジェクトのリスト
    """
    return db.query(Post)\
        .filter(Post.cast_id == cast_id, Post.deleted_at.is_(None))\
        .order_by(desc(Post.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()


def update_post(db: Session, post_id: int, body: Optional[str] = None, 
               photo_url: Optional[str] = None, status: Optional[str] = None) -> Optional[Post]:
    """
    投稿を更新する
    
    Args:
        db: データベースセッション
        post_id: 投稿ID
        body: 新しい投稿本文（任意）
        photo_url: 新しい画像のURL（任意）
        status: 新しい公開ステータス（任意）
    
    Returns:
        更新された投稿オブジェクトまたはNone
    """
    db_post = db.query(Post).filter(Post.id == post_id, Post.deleted_at.is_(None)).first()
    if not db_post:
        return None
    
    if body is not None:
        db_post.body = body
    if photo_url is not None:
        db_post.photo_url = photo_url
    if status is not None:
        db_post.status = status
    
    db.commit()
    db.refresh(db_post)
    return db_post


def delete_post(db: Session, post_id: int) -> bool:
    """
    投稿を論理削除する（deleted_atを設定）
    
    Args:
        db: データベースセッション
        post_id: 投稿ID
    
    Returns:
        削除成功ならTrue、失敗ならFalse
    """
    from datetime import datetime
    db_post = db.query(Post).filter(Post.id == post_id, Post.deleted_at.is_(None)).first()
    if not db_post:
        return False
    
    db_post.deleted_at = datetime.now()
    db.commit()
    return True


def increment_likes(db: Session, post_id: int) -> Optional[Post]:
    """
    投稿のいいね数をインクリメントする
    
    Args:
        db: データベースセッション
        post_id: 投稿ID
    
    Returns:
        更新された投稿オブジェクトまたはNone
    """
    db_post = db.query(Post).filter(Post.id == post_id, Post.deleted_at.is_(None)).first()
    if not db_post:
        return None
    
    db_post.likes_count += 1
    db.commit()
    db.refresh(db_post)
    return db_post
