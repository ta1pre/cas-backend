from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from enum import Enum

class TargetUserType(str, Enum):
    referrer = "referrer"
    referred = "referred"
    self = "self"
    other = "other"

class TransactionType(str, Enum):
    reservation_payment = "reservation_payment"
    reservation_reward = "reservation_reward"
    event_bonus = "event_bonus"
    coupon_bonus = "coupon_bonus"
    buyin = "buyin"
    referral_bonus_pending = "referral_bonus_pending"
    referral_bonus_completed = "referral_bonus_completed"

class PointType(str, Enum):
    regular = "regular"
    bonus = "bonus"
    pending = "pending"

class PointRuleResponse(BaseModel):
    """ポイントルール情報のレスポンススキーマ（管理画面用）"""
    id: int
    rule_name: str
    rule_description: Optional[str] = None
    event_type: str
    target_user_type: TargetUserType
    condition_data: Optional[Dict[str, Any]] = None
    transaction_type: TransactionType
    point_type: PointType
    point_value: float
    is_addition: bool = True
    additional_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    # is_activeフィールド（データベースから取得）
    is_active: bool = True
    
    class Config:
        from_attributes = True
        
    @property
    def status_text(self) -> str:
        """ステータステキスト"""
        return "有効" if self.is_active else "無効"
    
    @property
    def point_display(self) -> str:
        """ポイント表示用"""
        sign = "+" if self.is_addition else "-"
        return f"{sign}{int(self.point_value)}"

class PointRuleUpdateRequest(BaseModel):
    """ポイントルール更新リクエストスキーマ（管理画面用）"""
    rule_description: Optional[str] = Field(None, description="ルール説明")
    point_value: Optional[float] = Field(None, gt=0, description="ポイント数（正の値のみ）")
    is_addition: Optional[bool] = Field(None, description="加算フラグ")
    condition_data: Optional[Dict[str, Any]] = Field(None, description="条件データ")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="追加データ")
    is_active: Optional[bool] = Field(None, description="有効フラグ")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rule_description": "新規紹介時の仮ポイント付与",
                "point_value": 1000,
                "is_addition": True,
                "is_active": True
            }
        }