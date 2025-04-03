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
    """キャスト予約編集"""
    
    # ★ デバッグログ：受け取ったリクエストの内容を確認
    print(f"DEBUG - [サービス層 入口] 予約編集リクエスト受信: reservation_id={req.reservation_id}")
    print(f"DEBUG - [サービス層 入口] オプションID: {req.option_ids}")
    print(f"DEBUG - [サービス層 入口] カスタムオプション: {req.custom_options}")
    # フロントエンドからのoption_pointsを確認（existsattr関数でフィールドの存在確認）
    if hasattr(req, 'option_points'):
        print(f"DEBUG - [サービス層 入口] フロントエンドからのoption_points: {req.option_points}")
    else:
        print(f"DEBUG - [サービス層 入口] フロントエンドからoption_pointsは送信されていません")
    
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
    
    # ==========================================
    # ★ 処理順序を変更: オプション更新を先に行う
    # ==========================================
    # 4. オプションの全入れ替え
    print(f"DEBUG - [サービス層 Pre-Options] 予約ID={req.reservation_id}, オプション更新処理開始")
    print(f"DEBUG - [サービス層 Pre-Options] Reservationオブジェクト取得前 (まだDBから読み込んでいない、または前の状態)")
    print(f"DEBUG - [サービス層 Pre-Options] リクエストされた選択オプション: {req.option_ids}")
    print(f"DEBUG - [サービス層 Pre-Options] リクエストされたカスタムオプション数: {len(req.custom_options)}個")
    
    # カスタムオプションの詳細をログ出力
    for i, opt in enumerate(req.custom_options):
        print(f"DEBUG - [サービス層 Pre-Options] カスタムオプション #{i+1}: 名前={opt.name}, 価格={opt.price}")
    
    try:
        options_updated = update_reservation_options(
            db,
            req.reservation_id,
            req.option_ids,
            req.custom_options
        )
        
        if not options_updated:
            print(f"ERROR - [サービス層] オプション更新失敗: 予約ID={req.reservation_id}")
            # ★ オプション更新失敗時はロールバック
            db.rollback()
            return CastReservationEditResponse(
                success=False,
                message="オプションの更新に失敗しました",
                reservation_id=req.reservation_id
            )
        
        print(f"DEBUG - [サービス層 Post-Options] オプション更新成功: 予約ID={req.reservation_id}")
        # ★ オプション更新後の reservation オブジェクトの option_points を確認
        #   update_reservation_options内で更新されているはず
        updated_reservation_after_options = db.query(ResvReservation).filter(
            ResvReservation.id == req.reservation_id
        ).first() # 再度DBから取得するか、セッション内のオブジェクトを確認
        if updated_reservation_after_options:
            print(f"DEBUG - [サービス層 Post-Options] セッション内のoption_points: {updated_reservation_after_options.option_points}")
        else:
            print(f"WARN - [サービス層 Post-Options] オプション更新後、予約オブジェクトが見つかりません")

        # 追加デバッグログ
        print(f"DEBUG - [サービス層 Post-Options] リクエストにoption_pointsがあるか確認: {hasattr(req, 'option_points')}")
        
        # ★★★ フロントエンドから受け取ったoption_pointsを優先的に使用
        if hasattr(req, 'option_points') and req.option_points is not None:
            option_points = req.option_points
            print(f"DEBUG - [サービス層] フロントエンドから受け取ったoption_points: {option_points}を使用")
        else:
            # フロントエンドからoption_pointsが送られてこない場合はDBから計算
            from sqlalchemy import func
            from app.db.models.resv_reservation_option import ResvReservationOption
            option_points = db.query(func.sum(ResvReservationOption.option_price)).filter(
                ResvReservationOption.reservation_id == req.reservation_id,
                ResvReservationOption.status == "active"
            ).scalar() or 0
            print(f"DEBUG - [サービス層] DBから直接計算したoption_points: {option_points}")

    except Exception as e:
        print(f"ERROR - [サービス層] オプション更新例外発生: {str(e)}")
        # ★ 例外発生時もロールバック
        db.rollback()
        return CastReservationEditResponse(
            success=False,
            message=f"オプションの更新中にエラーが発生しました: {str(e)}",
            reservation_id=req.reservation_id
        )

    # ==========================================
    # ★ 次に予約本体の更新を行う
    # ==========================================
    # 2. 予約本体の更新
    print(f"DEBUG - [サービス層 Pre-Update] 予約本体更新処理開始: 予約ID={req.reservation_id}")
    # ★ 予約本体更新前の reservation オブジェクトの option_points を確認
    reservation_before_update = db.query(ResvReservation).filter(
        ResvReservation.id == req.reservation_id
    ).first()
    if reservation_before_update:
        print(f"DEBUG - [サービス層 Pre-Update] セッション内のoption_points: {reservation_before_update.option_points}")
    else:
         print(f"WARN - [サービス層 Pre-Update] 予約本体更新前、予約オブジェクトが見つかりません")
    
    reservation_data = {
        "reservation_id": req.reservation_id,
        "cast_id": req.cast_id,
        "course_id": req.course_id,
        "start_time": req.start_time,
        "end_time": req.end_time,  # ★ end_timeを追加（必要に応じてupdate_reservation内で再計算される）
        "location": req.location,
        "reservation_note": req.reservation_note,
        "status": "waiting_user_confirm", # ステータスをここで確定
        "transportation_fee": req.transportation_fee,
        "option_points": option_points  # ★★★ 重要な修正: DBから直接計算したoption_pointsを追加
    }
    
    print(f"DEBUG - [サービス層 Pre-Update] 更新データにoption_points={option_points}を追加")
    
    try:
        updated_reservation = update_reservation(
            db,
            reservation_data
        )
        
        if not updated_reservation:
            # ★ update_reservation内でエラーが発生した場合
            print(f"ERROR - [サービス層] 予約本体の更新失敗: 予約ID={req.reservation_id}")
            # ★ 予約更新失敗時もロールバック
            db.rollback()
            return CastReservationEditResponse(
                success=False,
                message="予約の更新に失敗しました",
                reservation_id=req.reservation_id
            )
        
        # ★ 予約本体更新後の reservation オブジェクトの option_points を確認
        reservation_after_update = db.query(ResvReservation).filter(
            ResvReservation.id == req.reservation_id
        ).first()
        if reservation_after_update:
            print(f"DEBUG - [サービス層 Post-Update] セッション内のoption_points: {reservation_after_update.option_points}")
        else:
             print(f"WARN - [サービス層 Post-Update] 予約本体更新後、予約オブジェクトが見つかりません")

    except Exception as e:
        # ★ update_reservation内で例外が発生した場合
        print(f"ERROR - [サービス層] 予約本体更新中に例外発生: {str(e)}")
        db.rollback()
        return CastReservationEditResponse(
            success=False,
            message=f"予約の更新中にエラーが発生しました: {str(e)}",
            reservation_id=req.reservation_id
        )

    # ==========================================
    # ★ 最後にステータス履歴を追加
    # ==========================================
    # 3. ステータス履歴の追加
    try:
        status_history = add_status_history(
            db,
            req.reservation_id,
            prev_status,
            new_status="waiting_user_confirm", # ここも確定させる
            changed_by="cast"
        )
        # ステータス履歴追加の失敗は致命的ではないかもしれないが、ログは残す
        if not status_history:
             print(f"WARN - [サービス層] ステータス履歴の追加に失敗: 予約ID={req.reservation_id}")
    except Exception as e:
        # ステータス履歴追加でエラーが起きても、予約更新自体は成功している可能性があるため、
        # ロールバックせずに警告ログのみ記録し、成功レスポンスを返すことを検討
        print(f"WARN - [サービス層] ステータス履歴追加中に例外発生: {str(e)}")

    # ==========================================
    # ★ すべて成功した場合、コミット
    # ==========================================
    print(f"DEBUG - [サービス層 Pre-Commit] コミット処理開始: 予約ID={req.reservation_id}")
    # ★ コミット直前の reservation オブジェクトの option_points を確認
    reservation_before_commit = db.query(ResvReservation).filter(
        ResvReservation.id == req.reservation_id
    ).first()
    if reservation_before_commit:
        print(f"DEBUG - [サービス層 Pre-Commit] セッション内のoption_points: {reservation_before_commit.option_points}")
    else:
         print(f"WARN - [サービス層 Pre-Commit] コミット直前、予約オブジェクトが見つかりません")

    try:
      db.commit()
      print(f"DEBUG - [サービス層] 予約編集完了、コミット成功: 予約ID={req.reservation_id}")
    except Exception as e:
      print(f"ERROR - [サービス層] 最終コミット中に例外発生: {str(e)}")
      db.rollback()
      return CastReservationEditResponse(
          success=False,
          message=f"データベースへの最終保存中にエラーが発生しました: {str(e)}",
          reservation_id=req.reservation_id
      )

    # 正常終了
    return CastReservationEditResponse(
        success=True,
        message="予約情報が更新されました。ユーザーの確認待ちです。",
        reservation_id=req.reservation_id
    )
