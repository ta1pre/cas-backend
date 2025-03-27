# 📂 app/features/reserve/repositories/cast/cast_options_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.point_details import PointDetailsOption, PointOptionMap
from app.db.models.resv_reservation_option import ResvReservationOption
from app.db.models.resv_reservation import ResvReservation

def get_available_options_for_cast(db: Session, cast_id: int):
    """
    キャストが対応可能なオプション一覧 (JOIN point_details_option)
    """
    stmt = (
        select(
            PointDetailsOption.id.label("option_id"),
            PointDetailsOption.option_name,
            PointDetailsOption.price.label("option_price")  # ✅ 正しくpriceに修正してalias
        )
        .join(PointOptionMap, PointOptionMap.option_id == PointDetailsOption.id)
        .where(
            PointOptionMap.cast_id == cast_id,
            PointOptionMap.is_active == True
            # ✅ PointDetailsOption.is_active は現状カラム無いため削除（必要ならDB追加）
        )
    )
    return db.execute(stmt).mappings().all()

def get_selected_options_by_reservation(db: Session, reservation_id: int):
    """
    指定した予約に紐づくオプション一覧 (マスター/自由入力どちらも)
    """
    stmt = (
        select(
            ResvReservationOption.option_id,
            ResvReservationOption.custom_name,
            ResvReservationOption.option_price
        )
        .where(
            ResvReservationOption.reservation_id == reservation_id,
            ResvReservationOption.status == "active"  # アクティブなオプションのみ取得
        )
    )
    return db.execute(stmt).mappings().all()


def check_belongs_to_cast(db: Session, reservation_id: int, cast_id: int) -> bool:
    """
    予約が本当にキャストの所有かチェック
    """
    stmt = (
        select(ResvReservation.id)
        .where(ResvReservation.id == reservation_id, ResvReservation.cast_id == cast_id)
    )
    result = db.execute(stmt).scalar()
    return True if result else False
