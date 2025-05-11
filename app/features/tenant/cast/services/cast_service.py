from sqlalchemy.orm import Session
import uuid
from app.db.models import user as user_model
from app.db.models.cast_common_prof import CastCommonProf
from ..schemas.cast import CastOut
from typing import List

def generate_line_id(tenant_id: int) -> str:
    return f"tenant_{tenant_id}_cast_{uuid.uuid4().hex}"

def register_cast(db: Session, nick_name: str, tenant_id: int) -> CastOut:
    new_user = user_model.User(
        nick_name=nick_name,
        line_id=f"tenant_{tenant_id}_cast_{uuid.uuid4().hex}",
        email_verified=False,
        phone_verified=False
    )
    db.add(new_user)
    db.commit()

    new_cast = CastCommonProf(
        cast_id=new_user.id,
        tenant=tenant_id,
        name=nick_name
    )
    db.add(new_cast)
    db.commit()
    
    return CastOut(
        id=new_cast.cast_id,
        name=new_cast.name,
        tenant=new_cast.tenant
    )

def fetch_casts_for_tenant(db: Session, tenant_id: int) -> List[CastOut]:
    casts = db.query(CastCommonProf).filter(
        CastCommonProf.tenant == tenant_id
    ).all()
    return [CastOut(
        id=cast.cast_id,
        name=cast.name,
        tenant=cast.tenant
    ) for cast in casts]

def update_cast_profile(db: Session, cast_id: int, nick_name: str, tenant_id: int) -> CastOut:
    cast = db.query(CastCommonProf).filter(
        CastCommonProf.cast_id == cast_id,
        CastCommonProf.tenant == tenant_id
    ).first()
    if not cast:
        raise ValueError("キャストが見つかりません")
    cast.name = nick_name
    db.commit()
    db.refresh(cast)
    return CastOut(
        id=cast.cast_id,
        name=cast.name,
        tenant=cast.tenant
    )
