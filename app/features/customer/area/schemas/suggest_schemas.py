from pydantic import BaseModel
from typing import Optional

class StationSuggestResponse(BaseModel):
    id: int
    name: str
    line_name: Optional[str] = "不明"
    line_id: Optional[int] = None
