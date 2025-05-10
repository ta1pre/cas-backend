from pydantic import BaseModel

class CastOut(BaseModel):
    id: int
    name: str
    tenant: int

    class Config:
        orm_mode = True

class CastCreate(BaseModel):
    nick_name: str
    # line_idは自動生成のため不要
