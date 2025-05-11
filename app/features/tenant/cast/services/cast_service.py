from sqlalchemy.orm import Session
import uuid
from app.db.models import user as user_model
from app.db.models.cast_common_prof import CastCommonProf
from ..schemas.cast import CastOut
from typing import List

def generate_line_id(tenant_id: int) -> str:
    return f"tenant_{tenant_id}_cast_{uuid.uuid4().hex}"

def register_cast(db: Session, cast: 'CastCreate', tenant_id: int) -> CastOut:
    new_user = user_model.User(
        nick_name=cast.name,
        line_id=f"tenant_{tenant_id}_cast_{uuid.uuid4().hex}",
        email_verified=False,
        phone_verified=False
    )
    db.add(new_user)
    db.commit()

    new_cast = CastCommonProf(
        cast_id=new_user.id,
        tenant=tenant_id,
        name=cast.name,
        age=cast.age,
        height=cast.height,
        bust=cast.bust,
        cup=cast.cup,
        waist=cast.waist,
        hip=cast.hip,
        birthplace=cast.birthplace,
        blood_type=cast.blood_type,
        hobby=cast.hobby,
        self_introduction=cast.self_introduction,
        job=cast.job,
        dispatch_prefecture=cast.dispatch_prefecture,
        support_area=cast.support_area,
        reservation_fee_deli=cast.reservation_fee_deli,
        is_active=cast.is_active,
        cast_type=cast.cast_type
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

def update_cast_profile(db: Session, cast_id: int, cast_data: 'CastCreate', tenant_id: int) -> CastOut:
    cast = db.query(CastCommonProf).filter(
        CastCommonProf.cast_id == cast_id,
        CastCommonProf.tenant == tenant_id
    ).first()
    if not cast:
        raise ValueError("キャストが見つかりません")
    cast.name = cast_data.name
    cast.age = cast_data.age
    cast.height = cast_data.height
    cast.bust = cast_data.bust
    cast.cup = cast_data.cup
    cast.waist = cast_data.waist
    cast.hip = cast_data.hip
    cast.birthplace = cast_data.birthplace
    cast.blood_type = cast_data.blood_type
    cast.hobby = cast_data.hobby
    cast.self_introduction = cast_data.self_introduction
    cast.job = cast_data.job
    cast.dispatch_prefecture = cast_data.dispatch_prefecture
    cast.support_area = cast_data.support_area
    cast.reservation_fee_deli = cast_data.reservation_fee_deli
    cast.is_active = cast_data.is_active
    cast.cast_type = cast_data.cast_type
    db.commit()
    db.refresh(cast)
    return CastOut(
        id=cast.cast_id,
        name=cast.name,
        tenant=cast.tenant
    )
