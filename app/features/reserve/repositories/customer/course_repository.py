from sqlalchemy.orm import Session
from app.db.models.point_details import PointDetailsCourse
from app.db.models.cast_common_prof import CastCommonProf

def get_courses_by_cast_id(cast_id: int, db: Session):
    """キャストIDから90分コースを取得"""
    cast = db.query(CastCommonProf).filter(CastCommonProf.cast_id == cast_id).first()
    if not cast:
        return []

    course_types = []
    if cast.cast_type in ["A", "AB"]:
        course_types.append(1)
    if cast.cast_type in ["B", "AB"]:
        course_types.append(2)

    return (
        db.query(PointDetailsCourse)
        .filter(PointDetailsCourse.course_type.in_(course_types))
        .filter(PointDetailsCourse.duration_minutes == 90)  # ✅ 90分コースを取得
        .all()
    )
