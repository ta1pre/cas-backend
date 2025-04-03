from pydantic import BaseModel

class CustomerCourseResponse(BaseModel):
    course_id: int  # コースIDを追加
    course_name: str
    duration: int  # `duration_minutes` に対応
    cost: int  # `cost_points` に対応
    course_type: int  # `course_type` を追加
    course_points: int = 0  # 予約テーブル用の時間料金
    reservation_fee: int = 0  # 予約テーブル用の予約料金

    class Config:
        orm_mode = True  # SQLAlchemyモデルとの互換性を確保
