"""Withdrawal endpoints"""
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.features.withdrawal.schemas.withdrawal_schema import (
    Withdrawal,
    WithdrawalCreate,
    PointBalanceInfo,
)
from app.features.withdrawal.services.withdrawal_service import WithdrawalService

withdrawal_router = APIRouter(
    dependencies=[Depends(get_current_user)],
    tags=["Withdrawal"],
)


@withdrawal_router.post("/request", response_model=Withdrawal, status_code=status.HTTP_201_CREATED)
def create_withdrawal_request(
    payload: WithdrawalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """キャストが出金申請を行う"""
    req = WithdrawalService.create_withdrawal(db, cast_id=current_user.id, payload=payload)
    db.commit()
    db.refresh(req)
    return req


@withdrawal_router.get("/me", response_model=List[Withdrawal])
def list_my_withdrawals(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """キャスト本人の申請履歴"""
    return WithdrawalService.list_my_withdrawals(db, cast_id=current_user.id, skip=skip, limit=limit)


@withdrawal_router.get("/balance", response_model=PointBalanceInfo)
def get_point_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """出金申請前のポイント残高取得"""
    return WithdrawalService.get_point_balance(db, cast_id=current_user.id)
