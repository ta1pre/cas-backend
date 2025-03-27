# ud83dudcc2 app/features/reserve/repositories/cast/cast_course_repository.py
from sqlalchemy.orm import Session
from app.db.models.cast_common_prof import CastCommonProf


def get_cast_type(db: Session, cast_id: int) -> str:
    """
    u30adu30e3u30b9u30c8u306eu30bfu30a4u30d7u3092u53d6u5f97u3059u308b
    
    Args:
        db (Session): DBu30bbu30c3u30b7u30e7u30f3
        cast_id (int): u30adu30e3u30b9u30c8ID
    
    Returns:
        str: u30adu30e3u30b9u30c8u30bfu30a4u30d7 ('A', 'B', 'AB', None)
    """
    cast = db.query(CastCommonProf).filter(CastCommonProf.cast_id == cast_id).first()
    if cast:
        return cast.cast_type
    return None
