from sqlalchemy.orm import Session
from ..repositories.cast_repository import get_casts_by_tenant
from ..schemas.cast import CastOut
from typing import List

def fetch_casts_for_tenant(db: Session, tenant_id: int) -> List[CastOut]:
    casts = get_casts_by_tenant(db, tenant_id)
    return [CastOut(
        id=cast.cast_id,
        name=cast.name,
        tenant=cast.tenant
    ) for cast in casts]
