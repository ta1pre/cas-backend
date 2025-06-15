from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta, timezone

from app.db.session import Base

# ✅ JST タイムゾーン定義
a_jst = timezone(timedelta(hours=9))

def jst_now():
    """Return current time in JST zone."""
    return datetime.now(a_jst)


class CastWithdrawalRequest(Base):
    """キャストの出金申請テーブル

    MySQL でのテーブル定義イメージ::

        CREATE TABLE cast_withdrawal_requests (
          id INT NOT NULL AUTO_INCREMENT COMMENT '主キー：出金申請ID',
          cast_id INT NOT NULL COMMENT 'キャストID（users.id）',
          amount INT NOT NULL COMMENT '出金申請額（ポイント＝円）',
          status ENUM('pending', 'approved', 'paid', 'rejected', 'cancelled') NOT NULL DEFAULT 'pending' COMMENT '申請ステータス',
          requested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '申請日時',
          approved_at DATETIME DEFAULT NULL COMMENT '承認日時',
          paid_at DATETIME DEFAULT NULL COMMENT '振込完了日時',
          rejected_at DATETIME DEFAULT NULL COMMENT '却下日時',
          cancelled_at DATETIME DEFAULT NULL COMMENT 'キャンセル日時',
          point_transaction_id INT DEFAULT NULL COMMENT 'ポイント履歴（pnt_point_transactions.id）との連携',
          account_snapshot JSON DEFAULT NULL COMMENT '申請時の口座情報（後から変更されても問題ないように）',
          admin_memo TEXT COMMENT '管理者メモ',
          is_deleted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '論理削除フラグ',
          PRIMARY KEY (id),
          FOREIGN KEY (cast_id) REFERENCES users(id),
          FOREIGN KEY (point_transaction_id) REFERENCES pnt_point_transactions(id)
        );
    """

    __tablename__ = "cast_withdrawal_requests"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主キー：出金申請ID")
    cast_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="キャストID（users.id）")
    amount = Column(Integer, nullable=False, comment="出金申請額（ポイント＝円）")
    regular_amount = Column(Integer, nullable=True, default=0, comment="通常ポイント出金申請額")
    bonus_amount = Column(Integer, nullable=True, default=0, comment="ボーナスポイント出金申請額")
    status = Column(
        Enum(
            "pending",
            "approved",
            "paid",
            "rejected",
            "cancelled",
            name="withdrawal_status_enum",
            create_constraint=True,
        ),
        nullable=False,
        default="pending",
        comment="申請ステータス",
    )

    requested_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, comment="申請日時"
    )
    approved_at = Column(DateTime(timezone=True), nullable=True, comment="承認日時")
    paid_at = Column(DateTime(timezone=True), nullable=True, comment="振込完了日時")
    rejected_at = Column(DateTime(timezone=True), nullable=True, comment="却下日時")
    cancelled_at = Column(DateTime(timezone=True), nullable=True, comment="キャンセル日時")

    point_transaction_id = Column(
        Integer,
        ForeignKey("pnt_point_transactions.id"),
        nullable=True,
        comment="ポイント履歴（pnt_point_transactions.id）との連携",
    )
    account_snapshot = Column(JSON, nullable=True, comment="申請時の口座情報（後から変更されても問題ないように）")
    admin_memo = Column(Text, nullable=True, comment="管理者メモ")
    is_deleted = Column(Boolean, nullable=False, default=False, comment="論理削除フラグ")

    # ✅ リレーション
    cast = relationship("User", backref="withdrawal_requests", foreign_keys=[cast_id])
    point_transaction = relationship(
        "PointTransaction", backref="withdrawal_request", foreign_keys=[point_transaction_id]
    )
