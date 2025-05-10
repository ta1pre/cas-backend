from pydantic import BaseModel

class CastOut(BaseModel):
    id: int
    name: str
    tenant: int

    class Config:
        orm_mode = True
