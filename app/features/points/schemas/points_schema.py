# app/features/points/schemas/points_schema.py
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

#points.py用 個別ポイント表示

class PointBalanceResponse(BaseModel):
    user_id: int
    regular_points: int
    bonus_points: int
    pending_points: int
    total_points: int

############# 履歴ポイント表示用 ############# 
# ✅ 履歴ポイント表示用
class PointHistoryItem(BaseModel):
    transaction_id: int
    transaction_type: str
    point_change: int
    point_source: str
    balance_after: int
    created_at: datetime
    rule_description: Optional[str] = None  # ✅ ルール説明を追加

# ✅ 履歴取得レスポンス
class PointHistoryResponse(BaseModel):
    history: List[PointHistoryItem]
    total_count: int

# ✅ 履歴取得リクエスト
class PointHistoryRequest(BaseModel):
    user_id: int
    limit: int = 5   # ✅ デフォルト5件
    offset: int = 0  # ✅ デフォルト0件目から

# ✅ 履歴取得レスポンス
class PointHistoryResponse(BaseModel):
    history: List[PointHistoryItem]
    total_count: int  # ✅ 全履歴件数 (ページネーション用)
    
class ApplyPointRuleRequest(BaseModel):
    user_id: int
    rule_name: str
    variables: Optional[Dict[str, int]] = None  # ✅ 追加の変数がある場合のみ送る

class ApplyPointRuleResponse(BaseModel):
    success: bool
    message: str
    transaction_id: Optional[int] = None  # ✅ 成功時にトランザクションIDを返す

class ReferredUserResponse(BaseModel):
    id: int
    nick_name: Optional[str]
    line_id: str
    created_at: datetime

    class Config:
        orm_mode = True
