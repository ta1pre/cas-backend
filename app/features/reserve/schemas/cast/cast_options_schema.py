# 📂 app/features/reserve/schemas/cast/cast_options_schema.py

from pydantic import BaseModel
from typing import Optional, List

class CastOptionRequest(BaseModel):
    """
    リクエスト: キャストが予約のオプション情報を取得したい
    """
    reservation_id: int
    cast_id: int

class AvailableOption(BaseModel):
    option_id: int
    option_name: str
    option_price: int

class SelectedMasterOption(BaseModel):
    option_id: int

class SelectedCustomOption(BaseModel):
    custom_option_name: str
    custom_option_price: int

class SelectedOption(BaseModel):
    """
    マスターと自由入力を混ぜるためのUnion表現にしたいが、
    pydanticで複雑になるので、簡易的に2フィールドで吸収
    """
    option_id: Optional[int] = None
    station_name: Optional[str] = None  # 駅IDの場合は駅名も返す
    custom_option_name: Optional[str] = None
    custom_option_price: Optional[int] = None

class CastOptionResponse(BaseModel):
    """
    レスポンス: キャスト向けオプション一覧
    """
    available_options: List[AvailableOption]
    selected_options: List[SelectedOption]
