import math # 時間料金計算のためにmathをインポート
from sqlalchemy.orm import Session
from app.features.reserve.repositories.customer.course_repository import get_courses_by_cast_id
from app.features.reserve.schemas.customer.customer_course_schema import CustomerCourseResponse
# キャストプロフィールを取得するリポジトリをインポート
from app.features.customer.castprof.repositories.castprof_repository import get_cast_profile


def get_available_courses_by_cast_id(cast_id: int, db: Session):
    """キャストIDをもとに 90 分コースを取得"""
    # まずキャストのプロフィール情報を取得
    cast_profile = get_cast_profile(cast_id, db)
    if not cast_profile:
        # キャスト情報が見つからない場合は空リストを返すかエラー処理
        # ここでは空リストを返す例
        return [] 

    # キャストの予約料金情報を取得
    reservation_fee = cast_profile.reservation_fee or 0
    reservation_fee_deli = cast_profile.reservation_fee_deli or reservation_fee # deliがなければ通常料金にフォールバック

    # キャストのコース一覧を取得
    courses = get_courses_by_cast_id(cast_id, db)
    
    response_courses = []
    for c in courses:
        # コースタイプに応じて基本料金を選択
        if c.course_type == 2: # SPコース
            base_fee = reservation_fee_deli
        else: # 通常コース
            base_fee = reservation_fee

        # 時間料金を計算 (時間 / 60) * 基本料金
        time_based_fee = (c.duration_minutes / 60) * base_fee
        
        # 表示用の最終料金 = 時間料金(2倍) + コース固有ポイント
        # 計算式: 2((コース時間 / 60) * 基本料金) + コース固有ポイント
        total_cost = 2 * time_based_fee + c.cost_points

        # デバッグ用：計算値を確認
        print(f"コースID: {c.id}, コース: {c.course_name}, 時間: {c.duration_minutes}分")
        print(f"基本料金: {base_fee}, 時間料金: {time_based_fee}")
        print(f"最終料金: {total_cost}, コース固有ポイント: {c.cost_points}")

        response_courses.append(
            CustomerCourseResponse(
                course_id=c.id,  # コースIDを追加
                course_name=c.course_name,
                duration=c.duration_minutes,
                cost=total_cost, # 計算した最終料金を設定
                course_type=c.course_type,
                # 予約テーブル用の値も設定
                course_points=c.cost_points,
                reservation_fee=time_based_fee  # 時間料金(基本料金×時間)を設定
            )
        )
        
    return response_courses
