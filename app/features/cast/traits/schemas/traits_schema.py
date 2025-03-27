from pydantic import BaseModel
from typing import List

# ✅ 特徴リストのレスポンス用モデル
class TraitResponse(BaseModel):
    id: int
    name: str
    weight: int
    category: str  
    is_active: int  

# ✅ キャスト ID をリクエストとして送る
class SelectedTraitsRequest(BaseModel):
    cast_id: int  

# ✅ キャストの特徴登録・削除リクエスト
class TraitRegisterRequest(BaseModel):
    cast_id: int
    trait_ids: List[int]
