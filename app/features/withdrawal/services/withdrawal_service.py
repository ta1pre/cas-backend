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
        if payload.regular_amount < 0 or payload.bonus_amount < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="出金額は0以上で入力してください")
        
        if payload.regular_amount > 0 and payload.regular_amount < MIN_WITHDRAWAL_AMOUNT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"通常ポイントの最低出金額は{MIN_WITHDRAWAL_AMOUNT}ポイントです")
        
        if payload.bonus_amount > 0 and payload.bonus_amount < MIN_WITHDRAWAL_AMOUNT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"ボーナスポイントの最低出金額は{MIN_WITHDRAWAL_AMOUNT}ポイントです")
        
        if payload.amount == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="出金額を入力してください")

        # 2. 残高チェック
        balance: PointBalance | None = db.query(PointBalance).filter(PointBalance.user_id == cast_id).first()
        if not balance:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ポイント残高が見つかりません")

        if payload.regular_amount > 0 and balance.regular_point_balance < payload.regular_amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="通常ポイントの残高が不足しています")
        
        if payload.bonus_amount > 0 and balance.bonus_point_balance < payload.bonus_amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ボーナスポイントの残高が不足しています")

        # 2. 申請レコード作成
        req = WithdrawalRepository.create(
            db,
            cast_id=cast_id,
            amount=payload.amount,
            account_snapshot=payload.account_snapshot,
        )

        # 3. ポイントを減算 (凍結や別管理にすべきだが簡略化)
        if payload.regular_amount > 0:
            balance.regular_point_balance -= payload.regular_amount
        if payload.bonus_amount > 0:
            balance.bonus_point_balance -= payload.bonus_amount
        balance.total_point_balance = balance.regular_point_balance + balance.bonus_point_balance
        db.add(balance)

        # 4. トランザクション履歴を追加
        transactions = []
        if payload.regular_amount > 0:
            pt_regular = PointTransaction(
                user_id=cast_id,
                point_change=-payload.regular_amount,
                balance_after=balance.total_point_balance,
                transaction_type="withdrawal_request",
                related_table="withdrawal",
                related_id=req.id,
                point_source="regular",
            )
            db.add(pt_regular)
            transactions.append(pt_regular)
        
        if payload.bonus_amount > 0:
            pt_bonus = PointTransaction(
                user_id=cast_id,
                point_change=-payload.bonus_amount,
                balance_after=balance.total_point_balance,
                transaction_type="withdrawal_request",
                related_table="withdrawal",
                related_id=req.id,
                point_source="bonus",
            )
            db.add(pt_bonus)
            transactions.append(pt_bonus)
        
        # 最初のトランザクションIDを記録（既存の互換性のため）
        if transactions:
            req.point_transaction_id = transactions[0].id
        db.add(req)

        return req

    @staticmethod
    def list_my_withdrawals(db: Session, *, cast_id: int, skip: int = 0, limit: int = 20):
        return WithdrawalRepository.get_by_cast(db, cast_id=cast_id, skip=skip, limit=limit)

    @staticmethod
    def get_point_balance(db: Session, *, cast_id: int) -> dict:
        """ポイント残高を取得"""
        balance: PointBalance | None = db.query(PointBalance).filter(PointBalance.user_id == cast_id).first()
        if not balance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ポイント残高が見つかりません")
        
        return {
            "regular_points": balance.regular_point_balance,
            "bonus_points": balance.bonus_point_balance,
            "total_points": balance.total_point_balance,
        }
