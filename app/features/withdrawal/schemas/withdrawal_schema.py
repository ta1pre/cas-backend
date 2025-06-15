from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


class WithdrawalBase(BaseModel):
    amount: int = Field(..., ge=1, description="出金申請額（ポイント＝円）")


class WithdrawalCreate(WithdrawalBase):
    amount: int = Field(..., ge=10000, description="出金申請額（ポイント＝円）(最低10,000pt)")
    point_source: Literal["regular", "bonus"] = Field(..., description="ポイント種別 (regular/bonus)")
    account_snapshot: Optional[dict] = Field(
        None, description="申請時の口座情報（省略時はユーザーに登録済みの情報を使用）"
    )


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

    class Config:
        orm_mode = True


class Withdrawal(WithdrawalInDBBase):
    pass
