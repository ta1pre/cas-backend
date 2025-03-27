from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime

from app.features.reserve.schemas.cast.cast_edit_schema import (
    CastReservationEditRequest,
    CastReservationEditResponse,
    CustomOption
)
from app.features.reserve.repositories.cast.cast_edit_repository import (
    verify_reservation_ownership,
    update_reservation,
    add_status_history,
    update_reservation_options
)
from app.db.models.resv_reservation import ResvReservation


def edit_reservation(
    db: Session,
    req: CastReservationEditRequest
) -> CastReservationEditResponse:
    """
    予約編集サービス
    
    処理フロー:
    1. 予約所有権確認（他人の予約は編集不可）
    2. 予約本体の更新
    3. ステータス履歴の追加（キャスト編集→ユーザー確認待ち）
    4. オプションの全入れ替え
    """
    
    # 1. 予約所有権確認
    if not verify_reservation_ownership(db, req.reservation_id, req.cast_id):
        return CastReservationEditResponse(
            success=False,
            message="指定された予約が見つからないか、この予約を編集する権限がありません",
            reservation_id=req.reservation_id
        )
    
    # 予約情報を取得（現在のステータスを記録するため）
    reservation = db.query(ResvReservation).filter(
        ResvReservation.id == req.reservation_id
    ).first()
    
    if not reservation:
        return CastReservationEditResponse(
            success=False,
            message="予約が見つかりません",
            reservation_id=req.reservation_id
        )
    
    prev_status = reservation.status
    
    # 2. 予約本体の更新
    reservation_data = {
        "reservation_id": req.reservation_id,
        "cast_id": req.cast_id,
        "course_id": req.course_id,
        "start_time": req.start_time,
        "end_time": req.end_time,
        "location": req.location,
        "reservation_note": req.reservation_note,
        "status": req.status
    }
    updated_reservation = update_reservation(
        db,
        reservation_data
    )
    
    if not updated_reservation:
        return CastReservationEditResponse(
            success=False,
            message="予約の更新に失敗しました",
            reservation_id=req.reservation_id
        )
    
    # 3. ステータス履歴の追加
    status_history = add_status_history(
        db,
        req.reservation_id,
        prev_status,
        new_status="waiting_user_confirm",
        changed_by="cast"
    )
    
    # 4. オプションの全入れ替え
    print(f"DEBUG - [サービス層] オプション更新処理開始: 予約ID={req.reservation_id}")
    print(f"DEBUG - [サービス層] 選択オプション: {req.option_ids}")
    print(f"DEBUG - [サービス層] カスタムオプション数: {len(req.custom_options)}個")
    
    # カスタムオプションの詳細をログ出力
    for i, opt in enumerate(req.custom_options):
        print(f"DEBUG - [サービス層] カスタムオプション #{i+1}: 名前={opt.name}, 価格={opt.price}")
    
    try:
        options_updated = update_reservation_options(
            db,
            req.reservation_id,
            req.option_ids,
            req.custom_options
        )
        
        if not options_updated:
            print(f"ERROR - [サービス層] オプション更新失敗: 予約ID={req.reservation_id}")
            return CastReservationEditResponse(
                success=False,
                message="オプションの更新に失敗しました",
                reservation_id=req.reservation_id
            )
        
        print(f"DEBUG - [サービス層] オプション更新成功: 予約ID={req.reservation_id}")
    except Exception as e:
        print(f"ERROR - [サービス層] オプション更新例外発生: {str(e)}")
        return CastReservationEditResponse(
            success=False,
            message=f"オプションの更新中にエラーが発生しました: {str(e)}",
            reservation_id=req.reservation_id
        )
    
    # 正常終了
    return CastReservationEditResponse(
        success=True,
        message="予約情報が更新されました。ユーザーの確認待ちです。",
        reservation_id=req.reservation_id
    )
