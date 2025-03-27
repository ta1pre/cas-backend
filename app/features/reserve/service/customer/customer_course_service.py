from sqlalchemy.orm import Session
from app.features.reserve.repositories.customer.course_repository import get_courses_by_cast_id
from app.features.reserve.schemas.customer.customer_course_schema import CustomerCourseResponse

def get_available_courses_by_cast_id(cast_id: int, db: Session):
    """キャストIDをもとに 90 分コースを取得"""
    courses = get_courses_by_cast_id(cast_id, db)

    return [
        CustomerCourseResponse(
            course_name=c.course_name,
            duration=c.duration_minutes,  # ✅ `duration_minutes` に修正
            cost=c.cost_points,  # ✅ `cost_points` に修正
            course_type=c.course_type  # ✅ `course_type` を追加
        )
        for c in courses
    ]
