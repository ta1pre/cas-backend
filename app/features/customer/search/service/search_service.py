from sqlalchemy.orm import Session
from app.features.customer.search.repositories.search_repository import get_casts

def fetch_cast_list(limit: int, offset: int, sort: str, filters: dict, db: Session):
    print(f"【バックエンド API 受信】 offset: {offset}, limit: {limit}, sort: {sort}, filters: {filters}")  # ✅ 確認用ログ

    # ✅ `filters` を `get_casts()` に渡す
    casts = get_casts(limit, offset, sort, filters, db)

    print(f"【取得データ】 {casts}")  # ✅ データ構造を確認

    return [
        {
            "cast_id": cast["cast_id"] if isinstance(cast, dict) else cast[0],  
            "name": cast["name"] if isinstance(cast, dict) else cast[1],
            "age": cast["age"] if isinstance(cast, dict) else cast[2],
            "profile_image_url": cast["profile_image_url"] if isinstance(cast, dict) else cast[3] if cast[3] else None,
            "height": cast["height"] if isinstance(cast, dict) else cast[4] if len(cast) > 4 else None,
            "bust": cast["bust"] if isinstance(cast, dict) else cast[5] if len(cast) > 5 else None,
            "waist": cast["waist"] if isinstance(cast, dict) else cast[6] if len(cast) > 6 else None,
            "hip": cast["hip"] if isinstance(cast, dict) else cast[7] if len(cast) > 7 else None,
            "cup": cast["cup"] if isinstance(cast, dict) else cast[8] if len(cast) > 8 else None,
            "birthplace": cast["birthplace"] if isinstance(cast, dict) else cast[9] if len(cast) > 9 else None,
            "support_area": cast["support_area"] if isinstance(cast, dict) else cast[10] if len(cast) > 10 else None,
            "blood_type": cast["blood_type"] if isinstance(cast, dict) else cast[11] if len(cast) > 11 else None,
            "hobby": cast["hobby"] if isinstance(cast, dict) else cast[12] if len(cast) > 12 else None,
            "job": cast["job"] if isinstance(cast, dict) else cast[13] if len(cast) > 13 else None,
            "reservation_fee": cast["reservation_fee"] if isinstance(cast, dict) else cast[14] if len(cast) > 14 else None,
            "rating": cast["rating"] if isinstance(cast, dict) else cast[15] if len(cast) > 15 else None,
            "self_introduction": cast["self_introduction"] if isinstance(cast, dict) else cast[18] if len(cast) > 18 else None,
            "popularity": cast["popularity"] if isinstance(cast, dict) else cast[16] if len(cast) > 16 else None,
            "available_at": cast["available_at"] if isinstance(cast, dict) else cast[17] if len(cast) > 17 else None,
        }
        for cast in casts
    ]
