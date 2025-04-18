from sqlalchemy import Column, Integer, ForeignKey, String, Enum, DateTime, Index, Float, Boolean, JSON, TIMESTAMP
from sqlalchemy.orm import relationship
from app.db.session import Base
from datetime import datetime, timedelta, timezone
from sqlalchemy.sql import func

# ✅ JST のタイムゾーンを定義
JST = timezone(timedelta(hours=9))

# ✅ ユーザーのポイント残高管理
class PointBalance(Base):
    __tablename__ = "pnt_user_point_balances"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)  # ✅ PRIMARY KEY（ユーザーID）
    regular_point_balance = Column(Integer, nullable=False, default=0)  # ✅ 通常ポイント
    bonus_point_balance = Column(Integer, nullable=False, default=0)  # ✅ ボーナスポイント
    total_point_balance = Column(Integer, nullable=False, default=0)  # ✅ 合計ポイント
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # ✅ 最終更新時刻

# ✅ ポイント取引履歴
class PointTransaction(Base):
    __tablename__ = "pnt_point_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)  # ✅ 取引ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # ✅ ユーザーID
    rule_id = Column(Integer, ForeignKey("pnt_details_rules.id", ondelete="SET NULL"), nullable=True)  # ✅ ルールID（外部キー）
    related_id = Column(Integer, nullable=True)  # ✅ 関連ID（予約IDなど）
    related_table = Column(Enum("reservation", "event", "coupon", "purchase", "manual_adjustment", name="related_table_enum"), nullable=True)  # ✅ 関連テーブル種別
    transaction_type = Column(Enum("deposit", "refund", "release", "event_bonus", "manual_adjustment", "purchase", "reservation_payment", name="transaction_type_enum"), nullable=False)  # ✅ 取引タイプ
    point_change = Column(Integer, nullable=False)  # ✅ 変更ポイント数
    point_source = Column(Enum("regular", "bonus", name="point_source_enum"), nullable=False, default="regular")  # ✅ ポイント種別
    balance_after = Column(Integer, nullable=False)  # ✅ 取引後の残高
    description = Column(String(255), nullable=True)  # ✅ 取引の説明（履歴表示用）
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ✅ ルールとのリレーション
    rule = relationship("PointRule", backref="transactions")

    # ✅ 高速検索用インデックス
    __table_args__ = (
        Index("idx_user_id", "user_id"),  # ✅ ユーザーごとの検索用
        Index("idx_related_id", "related_table", "related_id")  # ✅ 関連取引検索用
    )


# ✅ ポイントルールテーブル（pnt_details_rules）
class PointRule(Base):
    __tablename__ = "pnt_details_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(255), unique=True, nullable=False)  # ✅ ルール名（ユニーク）
    rule_description = Column(String(255), nullable=True)  # ✅ 説明
    transaction_type = Column(Enum('reservation_payment', 'reservation_reward', 'event_bonus', 'coupon_bonus', 'buyin'), nullable=False)
    point_type = Column(Enum('regular', 'bonus'), nullable=False)
    point_value = Column(Float, nullable=False)  # ✅ ポイント数
    is_addition = Column(Boolean, default=True)  # ✅ 加算(True) or 減算(False)
    additional_data = Column(JSON, nullable=True)  # ✅ 追加データ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
