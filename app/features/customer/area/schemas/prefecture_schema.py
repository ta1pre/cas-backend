# ファイル: app/schemas/prefecture_schema.py

from pydantic import BaseModel

class PrefectureSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True  # ORM モード

# ✅ 登録用スキーマ
class PrefectureRegisterSchema(BaseModel):
    user_id: int
    prefecture_id: int