from app.db.models import cast_common_prof
from sqlalchemy.orm import Session
from typing import List

# テナントIDからキャスト一覧を取得

def get_casts_by_tenant(db: Session, tenant_id: int) -> List[cast_common_prof.CastCommonProf]:
    return db.query(cast_common_prof.CastCommonProf).filter(cast_common_prof.CastCommonProf.tenant == tenant_id).all()
