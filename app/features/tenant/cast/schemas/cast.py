from pydantic import BaseModel

class CastOut(BaseModel):
    id: int
    name: str
    tenant: int

    class Config:
        orm_mode = True

class CastCreate(BaseModel):
    name: str
    age: int | None = None
    height: int | None = None
    bust: int | None = None
    cup: str | None = None
    waist: int | None = None
    hip: int | None = None
    birthplace: str | None = None
    blood_type: str | None = None
    hobby: str | None = None
    self_introduction: str | None = None
    job: str | None = None
    dispatch_prefecture: str | None = None
    support_area: str | None = None
    reservation_fee_deli: int | None = None
    is_active: int | None = None
    cast_type: str | None = None
    # 必要に応じて追加項目を拡張
