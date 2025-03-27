# app/features/customer/search/repositories/search_repository.py
from sqlalchemy.orm import aliased
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.db.models.cast_common_prof import CastCommonProf
from app.db.models.media_files import MediaFile  # ✅ メディアファイルのモデルをインポート
from app.db.models.prefectures import Prefecture

def get_casts(limit: int, offset: int, sort: str, filters: dict, db: Session):
    print(f"【リポジトリ】 offset: {offset}, limit: {limit}, sort: {sort}, filters: {filters}")

    PrefectureAlias1 = aliased(Prefecture)
    PrefectureAlias2 = aliased(Prefecture)
    MediaAlias = aliased(MediaFile)

    stmt = (
        select(
            CastCommonProf.cast_id,
            CastCommonProf.name,
            CastCommonProf.age,
            CastCommonProf.height,
            CastCommonProf.bust,
            CastCommonProf.waist,
            CastCommonProf.hip,
            CastCommonProf.cup,
            PrefectureAlias1.name.label("birthplace_name"),
            PrefectureAlias2.name.label("support_area_name"),
            CastCommonProf.blood_type,
            CastCommonProf.hobby,
            CastCommonProf.job,
            CastCommonProf.reservation_fee,
            CastCommonProf.rating,
            CastCommonProf.self_introduction, 
            CastCommonProf.popularity,
            CastCommonProf.available_at,
            MediaAlias.file_url.label("profile_image_url"),
        )
        .outerjoin(PrefectureAlias1, PrefectureAlias1.id == CastCommonProf.birthplace)
        .outerjoin(PrefectureAlias2, PrefectureAlias2.id == CastCommonProf.support_area)
        .outerjoin(
            MediaAlias,
            (CastCommonProf.cast_id == MediaAlias.target_id) &
            (MediaAlias.target_type == "profile_common") &
            (MediaAlias.order_index == 0)
        )
        .where(CastCommonProf.is_active == 1)
    )

    # ✅ `age` フィルターを適用
    # ✅ `min_age` / `max_age` に対応
    if "min_age" in filters and "max_age" in filters:
        min_age, max_age = filters["min_age"], filters["max_age"]
        stmt = stmt.where(CastCommonProf.age.between(min_age, max_age))
        print(f"【適用フィルター】 年齢: {min_age} ～ {max_age}")
            
    # ✅ 身長フィルター（追加）
    if "min_height" in filters and "max_height" in filters:
        min_height, max_height = filters["min_height"], filters["max_height"]
        stmt = stmt.where(CastCommonProf.height.between(min_height, max_height))
        print(f"【適用フィルター】 身長: {min_height} ～ {max_height}")

    # ✅ 指名料フィルター（追加）
    if "min_reservation_fee" in filters and "max_reservation_fee" in filters:
        min_fee, max_fee = filters["min_reservation_fee"], filters["max_reservation_fee"]
        stmt = stmt.where(CastCommonProf.reservation_fee.between(min_fee, max_fee))
        print(f"【適用フィルター】 指名料: {min_fee} ～ {max_fee}")
        
    # ✅ "今すぐOK" フィルター
    if "available_soon" in filters and filters["available_soon"]:
        stmt = stmt.where(CastCommonProf.available_at.isnot(None))  # `available_at` が NULL でない
        print("【適用フィルター】 今すぐOK（available_at IS NOT NULL）")
            
    # ✅ 都道府県フィルター（support_area に適用）
    if "prefecture_id" in filters:
        stmt = stmt.where(CastCommonProf.support_area == filters["prefecture_id"])
        print(f"【適用フィルター】 エリア（support_area）: {filters['prefecture_id']}")

    # ✅ キャストタイプフィルター
    if "cast_type" in filters:
        stmt = stmt.where(CastCommonProf.cast_type == filters["cast_type"])
        print(f"【適用フィルター】 キャストタイプ: {filters['cast_type']}")

    # 並べ替え条件
    sort_options = {
        "age_desc": CastCommonProf.age.desc(),
        "age_asc": CastCommonProf.age.asc(),
        "fee_desc": CastCommonProf.reservation_fee.desc(),
        "fee_asc": CastCommonProf.reservation_fee.asc(),
        "rating_desc": CastCommonProf.rating.desc(),
        "rating_asc": CastCommonProf.rating.asc(),
        "popularity_desc": CastCommonProf.popularity.desc(),
        "popularity_asc": CastCommonProf.popularity.asc(),
        "available_soon": CastCommonProf.available_at.desc(),
    }

    if sort in sort_options:
        stmt = stmt.order_by(sort_options[sort])
    else:
        stmt = stmt.order_by(CastCommonProf.cast_id)

    stmt = stmt.limit(limit).offset(offset)
    result = db.execute(stmt).all()

    # ✅ 返り値のデータを構造化
    casts = [
        {
            "cast_id": row.cast_id,
            "name": row.name,
            "age": row.age if row.age is not None else None,
            "height": row.height if row.height is not None else None,
            "bust": row.bust if row.bust is not None else None,
            "waist": row.waist if row.waist is not None else None,
            "hip": row.hip if row.hip is not None else None,
            "cup": row.cup if row.cup is not None else None,
            "birthplace": row.birthplace_name if row.birthplace_name is not None else None,
            "support_area": row.support_area_name if row.support_area_name is not None else None,
            "blood_type": row.blood_type if row.blood_type is not None else None,
            "hobby": row.hobby if row.hobby is not None else None,
            "job": row.job if row.job is not None else None,
            "reservation_fee": row.reservation_fee if row.reservation_fee is not None else 0,
            "rating": row.rating if row.rating is not None else 0.0,
            "self_introduction": row.self_introduction if row.self_introduction is not None else "",
            "popularity": row.popularity if row.popularity is not None else 0,
            "available_at": row.available_at if row.available_at is not None else None,
            "profile_image_url": row.profile_image_url if row.profile_image_url else "/default-avatar.png",
        }
        for row in result
    ]

    print(f"【リポジトリ戻り値】 {casts}")

    return casts
