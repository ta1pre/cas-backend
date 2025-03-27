# src/app/features/customer/search/schemas/user_schema.py

from pydantic import BaseModel

class UserPrefectureRequest(BaseModel):
    user_id: int
