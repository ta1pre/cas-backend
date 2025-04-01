from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PostBase(BaseModel):
    """投稿の基本情報"""
    body: str = Field(..., description="投稿本文")
    photo_url: Optional[str] = Field(None, description="投稿画像のURL（任意）")
    status: str = Field("public", description="公開ステータス（public/private/draft）")


class PostCreate(PostBase):
    """投稿作成リクエスト"""
    pass


class PostResponse(PostBase):
    """投稿情報レスポンス"""
    id: int = Field(..., description="投稿ID")
    cast_id: int = Field(..., description="キャストID")
    created_at: datetime = Field(..., description="投稿日時")
    updated_at: Optional[datetime] = Field(None, description="更新日時")
    likes_count: int = Field(0, description="いいね数")

    class Config:
        orm_mode = True


class PostUpdate(BaseModel):
    """投稿更新リクエスト"""
    id: int = Field(..., description="更新する投稿ID")
    body: Optional[str] = Field(None, description="投稿本文")
    photo_url: Optional[str] = Field(None, description="投稿画像のURL")
    status: Optional[str] = Field(None, description="公開ステータス（public/private/draft）")


class PostDelete(BaseModel):
    """投稿削除リクエスト"""
    id: int = Field(..., description="削除する投稿ID")


class PostDetail(BaseModel):
    """投稿詳細取得リクエスト"""
    id: int = Field(..., description="取得する投稿ID")


class PostLike(BaseModel):
    """投稿いいねリクエスト"""
    id: int = Field(..., description="いいねする投稿ID")
