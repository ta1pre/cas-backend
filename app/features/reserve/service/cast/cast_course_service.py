from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models.point_details import PointDetailsCourse, PointOptionMap
from app.db.models.cast_common_prof import CastCommonProf
from app.features.reserve.schemas.cast.cast_course_schema import (
    CastCourseListResponse,
    CourseResponse
)
from app.features.reserve.repositories.cast.cast_course_repository import get_cast_type
from app.features.reserve.repositories.common.price_calculator import calculate_reservation_points


def get_cast_courses(db: Session, cast_id: int) -> CastCourseListResponse:
    """
    キャストのコース一覧を取得する
    """
    # キャストのプロフィール情報を取得
    cast_profile = db.query(CastCommonProf).filter(CastCommonProf.cast_id == cast_id).first()
    if not cast_profile:
        # キャスト情報が見つからない場合は空リストを返す
        print(f"⚠️ 警告: cast_id={cast_id}のキャスト情報が見つかりません")
        return CastCourseListResponse(courses=[])
    
    # キャストの予約料金情報を取得してログ出力
    reservation_fee = cast_profile.reservation_fee or 0
    reservation_fee_deli = cast_profile.reservation_fee_deli or reservation_fee
    print(f"📊 キャスト料金情報: cast_id={cast_id}, reservation_fee={reservation_fee}, reservation_fee_deli={reservation_fee_deli}")
    
    courses_db = db.query(PointDetailsCourse).join(
        PointOptionMap, PointOptionMap.option_id == PointDetailsCourse.id
    ).filter(
        PointOptionMap.cast_id == cast_id,
        PointDetailsCourse.is_active == True,
        PointOptionMap.is_active == True
    ).all()
    
    courses = []
    for course in courses_db:
        # 共通の料金計算ロジックを使用
        try:
            points_data = calculate_reservation_points(
                db=db,
                course_id=course.id,
                cast_id=cast_id
            )
            
            # 計算結果をログ出力
            print(f"📊 コース計算結果: ID={course.id}, 名前={course.course_name}, タイプ={course.course_type}")
            print(f"   - 基本料金: {points_data['base_fee']}円/時")
            print(f"   - 時間: {course.duration_minutes}分")
            print(f"   - 予約料金: {points_data['reservation_fee']}ポイント")
            print(f"   - キャスト報酬: {points_data['cast_reward_points']}ポイント")
            
            # 計算されたポイントを使用
            cast_reward_points = points_data['cast_reward_points']
        except Exception as e:
            print(f"⚠️ 警告: コースID={course.id}の料金計算中にエラー: {str(e)}")
            # エラー時はデータベースの値をそのまま使用
            cast_reward_points = course.cast_reward_points
        
        courses.append(
            CourseResponse(
                id=course.id,
                course_name=course.course_name,
                description=course.description,
                duration_minutes=course.duration_minutes,
                cast_reward_points=cast_reward_points,
                course_type=course.course_type
            )
        )
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
    
    courses = []
    for course in courses_db:
        # データベースの値をそのまま使用（全コース一覧では計算しない）
        cast_reward_points = course.cast_reward_points
        
        # ポイントが0または未定義の場合は警告ログを出力
        if cast_reward_points is None or cast_reward_points == 0:
            print(f"⚠️ 警告: コースID={course.id}のcast_reward_pointsが{cast_reward_points}です。データを確認してください。")
        
        courses.append(
            CourseResponse(
                id=course.id,
                course_name=course.course_name,
                description=course.description,
                duration_minutes=course.duration_minutes,
                cast_reward_points=cast_reward_points,
                course_type=course.course_type
            )
        )
    
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
    cast_profile = None
    if cast_id:
        cast_type = get_cast_type(db, cast_id)
        print(f"DEBUG - キャストタイプ: {cast_type}")
        
        # キャストのプロフィール情報を取得
        cast_profile = db.query(CastCommonProf).filter(CastCommonProf.cast_id == cast_id).first()
        if cast_profile:
            # キャストの予約料金情報を取得してログ出力
            reservation_fee = cast_profile.reservation_fee or 0
            reservation_fee_deli = cast_profile.reservation_fee_deli or reservation_fee
            print(f"📊 キャスト料金情報: cast_id={cast_id}, reservation_fee={reservation_fee}, reservation_fee_deli={reservation_fee_deli}")
    
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
    
    courses = []
    for course in courses_db:
        if cast_id and cast_profile:
            # 共通の料金計算ロジックを使用
            try:
                points_data = calculate_reservation_points(
                    db=db,
                    course_id=course.id,
                    cast_id=cast_id
                )
                
                # 計算結果をログ出力
                print(f"📊 コース計算結果: ID={course.id}, 名前={course.course_name}, タイプ={course.course_type}")
                print(f"   - 基本料金: {points_data['base_fee']}円/時")
                print(f"   - 時間: {course.duration_minutes}分")
                print(f"   - 予約料金: {points_data['reservation_fee']}ポイント")
                print(f"   - キャスト報酬: {points_data['cast_reward_points']}ポイント")
                
                # 計算されたポイントを使用
                cast_reward_points = points_data['cast_reward_points']
            except Exception as e:
                print(f"⚠️ 警告: コースID={course.id}の料金計算中にエラー: {str(e)}")
                # エラー時はデータベースの値をそのまま使用
                cast_reward_points = course.cast_reward_points
        else:
            # キャストIDが指定されていない場合はデータベースの値をそのまま使用
            cast_reward_points = course.cast_reward_points
            
            # ポイントが0または未定義の場合は警告ログを出力
            if cast_reward_points is None or cast_reward_points == 0:
                print(f"⚠️ 警告: コースID={course.id}のcast_reward_pointsが{cast_reward_points}です。データを確認してください。")
        
        courses.append(
            CourseResponse(
                id=course.id,
                course_name=course.course_name,
                description=course.description,
                duration_minutes=course.duration_minutes,
                cast_reward_points=cast_reward_points,
                course_type=course.course_type
            )
        )
    
    return CastCourseListResponse(courses=courses)
