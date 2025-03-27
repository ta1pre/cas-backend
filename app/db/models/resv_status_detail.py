from sqlalchemy import Column, String, Text, Integer
from app.db.session import Base

class ResvStatusDetail(Base):
    __tablename__ = "resv_status_detail"

    status_key = Column(String(50), primary_key=True, comment="予約のステータスキー（例: requested, confirmed）")
    user_label = Column(String(50), nullable=False, comment="ユーザー向け表示文言")
    cast_label = Column(String(50), nullable=False, comment="キャスト向け表示文言")
    description = Column(Text, comment="ステータスの説明（例: ユーザーが予約をリクエストした状態）")
    display_order = Column(Integer, nullable=False, comment="表示順（例: 1=リクエスト中, 2=確定, 3=完了）")
    color_code = Column(String(7), nullable=True, comment="ステータスの表示カラー（例: #FF0000）")
