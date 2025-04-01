from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.security import get_current_user
from app.db.session import get_db
from app.features.posts.schemas.post_schema import PostCreate, PostResponse, PostUpdate, PostDelete, PostLike, PostDetail
from app.features.posts.services.post_service import (
    create_post_service,
    get_post_service,
    get_cast_posts_service,
    update_post_service,
    delete_post_service,
    like_post_service
)

router = APIRouter()


@router.post("/create", response_model=PostResponse)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    新しい投稿を作成する
    
    Args:
        post_data: 投稿データ
        db: データベースセッション
        current_user: 認証済みユーザーID
    
    Returns:
        作成された投稿情報
    """
    try:
        # 現在のユーザーIDをキャストIDとして使用
        cast_id = current_user
        
        # 投稿を作成
        db_post = create_post_service(db=db, cast_id=cast_id, post_data=post_data)
        
        return db_post
    except Exception as e:
        print(f"[ERROR] 投稿作成エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"投稿の作成に失敗しました: {str(e)}")


@router.post("/cast", response_model=List[PostResponse])
def get_cast_posts(
    cast_id: int = Body(...),
    skip: int = Body(0),
    limit: int = Body(20),
    db: Session = Depends(get_db),
    current_user: Optional[int] = Depends(get_current_user)
):
    """
    キャストの投稿一覧を取得する
    
    Args:
        cast_id: キャストID
        skip: スキップする件数
        limit: 取得件数上限
        db: データベースセッション
        current_user: 認証済みユーザーID
    
    Returns:
        投稿のリスト
    """
    try:
        posts = get_cast_posts_service(db=db, cast_id=cast_id, skip=skip, limit=limit)
        return posts
    except Exception as e:
        print(f"[ERROR] 投稿一覧取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"投稿一覧の取得に失敗しました: {str(e)}")


@router.post("/detail", response_model=PostResponse)
def get_post(
    post_data: PostDetail,
    db: Session = Depends(get_db),
    current_user: Optional[int] = Depends(get_current_user)
):
    """
    投稿の詳細を取得する
    
    Args:
        post_data: 投稿ID
        db: データベースセッション
        current_user: 認証済みユーザーID
    
    Returns:
        投稿の詳細情報
    """
    db_post = get_post_service(db=db, post_id=post_data.id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    return db_post


@router.post("/update", response_model=PostResponse)
def update_post(
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    投稿を更新する
    
    Args:
        post_data: 更新データ
        db: データベースセッション
        current_user: 認証済みユーザーID
    
    Returns:
        更新された投稿情報
    """
    # 投稿が存在するか確認
    db_post = get_post_service(db=db, post_id=post_data.id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    
    # 投稿の所有者かどうか確認
    if db_post.cast_id != current_user:
        raise HTTPException(status_code=403, detail="この投稿を更新する権限がありません")
    
    # 投稿を更新
    updated_post = update_post_service(db=db, post_id=post_data.id, post_data=post_data)
    if updated_post is None:
        raise HTTPException(status_code=500, detail="投稿の更新に失敗しました")
    
    return updated_post


@router.post("/delete")
def delete_post(
    post_data: PostDelete,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    投稿を削除する
    
    Args:
        post_data: 削除する投稿ID
        db: データベースセッション
        current_user: 認証済みユーザーID
    
    Returns:
        削除結果
    """
    # 投稿が存在するか確認
    db_post = get_post_service(db=db, post_id=post_data.id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    
    # 投稿の所有者かどうか確認
    if db_post.cast_id != current_user:
        raise HTTPException(status_code=403, detail="この投稿を削除する権限がありません")
    
    # 投稿を削除
    success = delete_post_service(db=db, post_id=post_data.id)
    if not success:
        raise HTTPException(status_code=500, detail="投稿の削除に失敗しました")
    
    return {"status": "success", "message": "投稿が削除されました"}


@router.post("/like", response_model=PostResponse)
def like_post(
    post_data: PostLike,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    投稿にいいねをする
    
    Args:
        post_data: 投稿ID
        db: データベースセッション
        current_user: 認証済みユーザーID
    
    Returns:
        更新された投稿情報
    """
    # 投稿が存在するか確認
    db_post = get_post_service(db=db, post_id=post_data.id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    
    # いいねを増やす
    updated_post = like_post_service(db=db, post_id=post_data.id)
    if updated_post is None:
        raise HTTPException(status_code=500, detail="いいねの追加に失敗しました")
    
    return updated_post
