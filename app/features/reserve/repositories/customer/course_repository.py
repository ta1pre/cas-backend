from sqlalchemy.orm import Session
from app.db.models.point_details import PointDetailsCourse
from app.db.models.cast_common_prof import CastCommonProf

def get_courses_by_cast_id(cast_id: int, db: Session):
    """キャストIDからコースを取得（時間制限なし）"""
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
        # ✅ コースの制限を削除
        .order_by(PointDetailsCourse.course_type, PointDetailsCourse.duration_minutes)  # ✅ コースタイプと時間順にソート
        .all()
    )
