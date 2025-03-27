from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models.point_details import PointDetailsCourse, PointOptionMap
from app.features.reserve.schemas.cast.cast_course_schema import (
    CastCourseListResponse,
    CourseResponse
)
from app.features.reserve.repositories.cast.cast_course_repository import get_cast_type


def get_cast_courses(db: Session, cast_id: int) -> CastCourseListResponse:
    """
    キャストのコース一覧を取得する
    """
    courses_db = db.query(PointDetailsCourse).join(
        PointOptionMap, PointOptionMap.option_id == PointDetailsCourse.id
    ).filter(
        PointOptionMap.cast_id == cast_id,
        PointDetailsCourse.is_active == True,
        PointOptionMap.is_active == True
    ).all()
    
    courses = [
        CourseResponse(
            id=course.id,
            course_name=course.course_name,
            description=course.description,
            duration_minutes=course.duration_minutes,
            cast_reward_points=course.cast_reward_points,
            course_type=course.course_type
        )
        for course in courses_db
    ]
    return CastCourseListResponse(courses=courses)

def get_all_courses(db: Session) -> CastCourseListResponse:
    """
    全てのアクティブなコース一覧を取得する
    """
    # デバッグログを追加
    print(f"DEBUG - 全コース取得処理開始")
    
    # 全てのアクティブなコースを取得、duration_minutesで並べ替え
    courses_db = db.query(PointDetailsCourse).filter(
        PointDetailsCourse.is_active == True
    ).order_by(PointDetailsCourse.duration_minutes).all()
    
    # デバッグログ
    print(f"DEBUG - 全アクティブコース数: {len(courses_db)}")
    
    courses = [
        CourseResponse(
            id=course.id,
            course_name=course.course_name,
            description=course.description,
            duration_minutes=course.duration_minutes,
            cast_reward_points=course.cast_reward_points,
            course_type=course.course_type
        )
        for course in courses_db
    ]
    
    # デバッグログ
    print(f"DEBUG - 返却コース数: {len(courses)}")
    for course in courses:
        print(f"DEBUG - コース情報: ID={course.id}, 名前={course.course_name}, タイプ={course.course_type}, 時間={course.duration_minutes}, ポイント={course.cast_reward_points}")
    
    return CastCourseListResponse(courses=courses)

def get_filtered_courses(db: Session, cast_id: int = None) -> CastCourseListResponse:
    """
    キャストタイプに基づいてフィルタリングされたコース一覧を取得する
    
    Args:
        db (Session): DBセッション
        cast_id (int, optional): キャストID。指定された場合、そのキャストのタイプに合わせてフィルタリング
    
    Returns:
        CastCourseListResponse: フィルタリングされたコース一覧
    """
    # デバッグログ
    print(f"DEBUG - フィルタリングコース取得処理開始 cast_id={cast_id}")
    
    # キャストIDが指定されている場合、キャストタイプを取得
    cast_type = None
    if cast_id:
        cast_type = get_cast_type(db, cast_id)
        print(f"DEBUG - キャストタイプ: {cast_type}")
    
    # 基本クエリ: アクティブなコースのみ
    query = db.query(PointDetailsCourse).filter(PointDetailsCourse.is_active == True)
    
    # キャストタイプに基づいてフィルタリング
    if cast_type:
        if cast_type == 'A':
            # Aタイプのキャストは、タイプ1のコースのみ提供可能
            query = query.filter(PointDetailsCourse.course_type == 1)
        elif cast_type == 'B':
            # Bタイプのキャストは、タイプ2のコースのみ提供可能
            query = query.filter(PointDetailsCourse.course_type == 2)
        elif cast_type == 'AB':
            # ABタイプのキャストは、両方のタイプのコースを提供可能
            # フィルタリングは不要
            pass
    
    # duration_minutesで並べ替え
    courses_db = query.order_by(PointDetailsCourse.duration_minutes).all()
    
    # デバッグログ
    print(f"DEBUG - フィルタリング後のコース数: {len(courses_db)}")
    
    # レスポンス形式に変換
    courses = [
        CourseResponse(
            id=course.id,
            course_name=course.course_name,
            description=course.description,
            duration_minutes=course.duration_minutes,
            cast_reward_points=course.cast_reward_points,
            course_type=course.course_type
        )
        for course in courses_db
    ]
    
    # デバッグログ
    for course in courses:
        print(f"DEBUG - フィルタリング後コース情報: ID={course.id}, 名前={course.course_name}, タイプ={course.course_type}, 時間={course.duration_minutes}, ポイント={course.cast_reward_points}")
    
    return CastCourseListResponse(courses=courses)
