# app/features/customer/castprof/service/castprof_service.py
from sqlalchemy.orm import Session
from app.features.customer.castprof.repositories.castprof_repository import get_cast_profile
from app.features.customer.castprof.repositories.image_repository import get_cast_images
from app.features.customer.castprof.service.cast_traits_service import fetch_cast_traits
from app.features.customer.castprof.service.cast_servicetype_service import fetch_cast_servicetypes
from app.features.customer.castprof.schemas.castprof_schema import CastProfileResponse

def fetch_cast_profile(cast_id: int, db: Session) -> CastProfileResponse:
    """キャストのプロフィール情報を取得し、Traits・ServiceTypes・画像を追加"""
    cast = get_cast_profile(cast_id, db)
    
    if not cast:
        return None

    # ✅ 画像データを取得
    images = get_cast_images(cast_id, db)

    # ✅ Traits（特徴）データを取得
    traits = fetch_cast_traits(cast_id, db)

    # ✅ ServiceTypes（サービス種別）データを取得
    service_types = fetch_cast_servicetypes(cast_id, db)

    # ✅ `dict()` に変換し、追加データを格納
    cast_dict = cast.__dict__
    cast_dict["images"] = images
    cast_dict["traits"] = traits
    cast_dict["service_types"] = service_types

    return CastProfileResponse(**cast_dict)
