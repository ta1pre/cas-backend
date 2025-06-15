from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.models.cast_withdrawal_requests import CastWithdrawalRequest


class WithdrawalRepository:
    """DB操作を担当するリポジトリ"""

    @staticmethod
    def create(db: Session, *, cast_id: int, amount: int, account_snapshot: Optional[dict] = None) -> CastWithdrawalRequest:
        obj = CastWithdrawalRequest(
            cast_id=cast_id,
            amount=amount,
            account_snapshot=account_snapshot or {},
        )
        db.add(obj)
        db.flush()  # id を取得
        return obj

    @staticmethod
    def get_by_cast(db: Session, *, cast_id: int, skip: int = 0, limit: int = 20) -> List[CastWithdrawalRequest]:
        q = (
            db.query(CastWithdrawalRequest)
            .filter(CastWithdrawalRequest.cast_id == cast_id, CastWithdrawalRequest.is_deleted == False)
            .order_by(CastWithdrawalRequest.requested_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return q.all()
