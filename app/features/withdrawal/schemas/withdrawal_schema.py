from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


class WithdrawalBase(BaseModel):
    amount: int = Field(..., ge=0, description="出金申請額（ポイント＝円）")


class WithdrawalCreate(BaseModel):
    regular_amount: int = Field(0, ge=0, description="通常ポイント出金申請額（ポイント＝円）")
    bonus_amount: int = Field(0, ge=0, description="ボーナスポイント出金申請額（ポイント＝円）")
    account_snapshot: Optional[dict] = Field(
        None, description="申請時の口座情報（省略時はユーザーに登録済みの情報を使用）"
    )
    
    @property
    def amount(self) -> int:
        return self.regular_amount + self.bonus_amount


class WithdrawalInDBBase(WithdrawalBase):
    id: int
    cast_id: int
    status: str
    requested_at: datetime
    approved_at: Optional[datetime]
    paid_at: Optional[datetime]
    rejected_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    account_snapshot: Optional[dict]
    admin_memo: Optional[str]
    regular_amount: Optional[int] = Field(None, description="通常ポイント出金申請額")
    bonus_amount: Optional[int] = Field(None, description="ボーナスポイント出金申請額")

    class Config:
        orm_mode = True


class Withdrawal(WithdrawalInDBBase):
    pass


class PointBalanceInfo(BaseModel):
    regular_points: int = Field(..., description="通常ポイント")
    bonus_points: int = Field(..., description="ボーナスポイント")  
    total_points: int = Field(..., description="合計ポイント")

    class Config:
        orm_mode = True
