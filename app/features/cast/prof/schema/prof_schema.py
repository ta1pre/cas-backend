# Cast Profile Schemas

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class CastProfBase(BaseModel):
    cast_type: Optional[Literal['A', 'B', 'AB']] = Field(None, description="キャストタイプ")
    name: Optional[str] = Field(None, max_length=255, description="名前")
    age: Optional[int] = Field(None, ge=18, description="年齢") # 最低年齢を仮定
    height: Optional[int] = Field(None, ge=100, le=250, description="身長(cm)") # 範囲を仮定
    bust: Optional[int] = Field(None, ge=50, le=150, description="バスト(cm)") # 範囲を仮定
    cup: Optional[str] = Field(None, max_length=10, description="カップ") # 文字数制限を仮定
    waist: Optional[int] = Field(None, ge=40, le=120, description="ウエスト(cm)") # 範囲を仮定
    hip: Optional[int] = Field(None, ge=50, le=150, description="ヒップ(cm)") # 範囲を仮定
    birthplace: Optional[str] = Field(None, max_length=255, description="出身地")
    blood_type: Optional[str] = Field(None, max_length=10, description="血液型")
    hobby: Optional[str] = Field(None, max_length=255, description="趣味")
    reservation_fee: Optional[int] = Field(None, ge=0, description="予約料金") # マイナス値不可
    self_introduction: Optional[str] = Field(None, max_length=255, description="自己紹介")
    job: Optional[str] = Field(None, max_length=255, description="職業")
    dispatch_prefecture: Optional[str] = Field(None, max_length=255, description="派遣可能都道府県")
    support_area: Optional[str] = Field(None, max_length=255, description="対応可能エリア")

class CastProfRead(CastProfBase):
    cast_id: int = Field(..., description="キャストID")
    rank_id: Optional[int] = Field(None, description="ランクID")
    popularity: int = Field(..., description="人気度")
    rating: float = Field(..., description="評価")
    is_active: Optional[int] = Field(None, description="アクティブ状態")
    available_at: Optional[datetime] = Field(None, description="利用可能日時")
    created_at: Optional[datetime] = Field(None, description="作成日時")
    updated_at: Optional[datetime] = Field(None, description="更新日時")
    station_name: Optional[str] = Field(None, description="駅名")  # 駅名フィールドを追加

    class Config:
        orm_mode = True # SQLAlchemyモデルから自動変換


class CastProfUpdate(CastProfBase):
    # CastProfBaseのフィールドを更新可能とする
    pass
