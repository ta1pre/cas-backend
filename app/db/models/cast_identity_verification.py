# u2705 cast_identity_verification.py - u30adu30e3u30b9u30c8u672cu4ebau78bau8a8du7ba1u7406u30e2u30c7u30eb
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from app.db.session import Base

class CastIdentityVerification(Base):
    __tablename__ = "cast_identity_verification"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cast_id = Column(Integer, ForeignKey("cast_common_prof.cast_id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum('unsubmitted', 'pending', 'approved', 'rejected'), nullable=False, default='unsubmitted')
    service_type = Column(Enum('A', 'B', 'AB'), nullable=False, default='A')  # u30b5u30fcu30d3u30b9u7a2eu5225
    id_photo_media_id = Column(Integer, nullable=True)  # u8eabu5206u8a3cu306eu30e1u30c7u30a3u30a2ID
    juminhyo_media_id = Column(Integer, nullable=True)  # u4f4fu6c11u7968u306eu30e1u30c7u30a3u30a2ID
    document_type = Column(String(50), nullable=True)  # 身分証の種類 (license, mynumber, passport, basic_resident_card)
    
    # 口座情報フィールド（将来のために保持、現在は使用しない）
    # bank_name = Column(String(100), nullable=True)  # 銀行名（例：みずほ銀行）
    # branch_name = Column(String(100), nullable=True)  # 支店名（例：渋谷支店）
    # branch_code = Column(String(10), nullable=True)  # 支店コード（3桁、例：123）
    # account_type = Column(String(20), nullable=True)  # 普通・当座など（例：普通）
    # account_number = Column(String(20), nullable=True)  # 口座番号（例：1234567）
    # account_holder = Column(String(100), nullable=True)  # 口座名義人（例：ヤマダ タロウ）
    
    submitted_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_id = Column(Integer, nullable=True)  # u5be9u67fbu8005ID
    rejection_reason = Column(String(500), nullable=True)  # u5374u4e0bu7406u7531
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_cast_id", "cast_id"),  # u30adu30e3u30b9u30c8IDu3067u306eu9ad8u901fu691cu7d22u7528u30a4u30f3u30c7u30c3u30afu30b9
        Index("idx_status", "status"),   # u30b9u30c6u30fcu30bfu30b9u3067u306eu691cu7d22u7528u30a4u30f3u30c7u30c3u30afu30b9
    )
