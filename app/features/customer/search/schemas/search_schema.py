from pydantic import BaseModel
from typing import Optional, Dict, Any  

class SearchRequest(BaseModel):
    limit: int
    offset: int
    sort: Optional[str] = "age_desc"
    filters: Optional[Dict[str, Any]] = {} 
