from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models.point import PointBalance, PointTransaction
from app.db.models.cast_withdrawal_requests import CastWithdrawalRequest
from app.features.withdrawal.repositories.withdrawal_repository import WithdrawalRepository
from app.features.withdrawal.schemas.withdrawal_schema import WithdrawalCreate

MIN_WITHDRAWAL_AMOUNT = 10000


class WithdrawalService:
    """ビジネスロジックを集約するサービスレイヤー"""

    @staticmethod
    def create_withdrawal(
        db: Session,
        *,
        cast_id: int,
        payload: WithdrawalCreate,
    ) -> CastWithdrawalRequest:
        # 1. 入力バリデーション
        if payload.amount < MIN_WITHDRAWAL_AMOUNT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"最低出金額は{MIN_WITHDRAWAL_AMOUNT}ポイントです")

        if payload.point_source not in ("regular", "bonus"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不正なポイント種別です")

        # 2. 残高チェック
        balance: PointBalance | None = db.query(PointBalance).filter(PointBalance.user_id == cast_id).first()
        if not balance:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ポイント残高が見つかりません")

        available = balance.regular_point_balance if payload.point_source == "regular" else balance.bonus_point_balance
        if available < payload.amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="残高が不足しています")

        # 2. 申請レコード作成
        req = WithdrawalRepository.create(
            db,
            cast_id=cast_id,
            amount=payload.amount,
            account_snapshot=payload.account_snapshot,
        )

        # 3. ポイントを減算 (凍結や別管理にすべきだが簡略化)
        if payload.point_source == "regular":
            balance.regular_point_balance -= payload.amount
        else:
            balance.bonus_point_balance -= payload.amount
        balance.total_point_balance = balance.regular_point_balance + balance.bonus_point_balance
        db.add(balance)

        # 4. トランザクション履歴を追加
        pt = PointTransaction(
            user_id=cast_id,
            point_change=-payload.amount,
            balance_after=balance.total_point_balance,
            transaction_type="withdrawal_request",
            related_table="withdrawal",
            related_id=req.id,
            point_source=payload.point_source,
        )
        db.add(pt)
        req.point_transaction_id = pt.id
        db.add(req)

        return req

    @staticmethod
    def list_my_withdrawals(db: Session, *, cast_id: int, skip: int = 0, limit: int = 20):
        return WithdrawalRepository.get_by_cast(db, cast_id=cast_id, skip=skip, limit=limit)
