# 📂 app/features/reserve/schemas/cast/cast_course_schema.py
from pydantic import BaseModel, Field
from typing import List

class CourseResponse(BaseModel):
    """コース情報レスポンススキーマ"""
    id: int = Field(..., description="コースID")
    course_name: str = Field(..., description="コース名")
    description: str = Field(None, description="コース詳細")
    duration_minutes: int = Field(..., description="コース時間")
    cast_reward_points: int = Field(..., description="キャスト報酬ポイント")
    course_type: int = Field(None, description="コースタイプ")

class CastCourseListResponse(BaseModel):
    """キャストコース一覧レスポンススキーマ"""
    courses: List[CourseResponse]
