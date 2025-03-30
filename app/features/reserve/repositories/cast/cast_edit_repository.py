from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.db.models.resv_reservation import ResvReservation
from app.db.models.resv_status_history import ResvStatusHistory
from app.db.models.resv_reservation_option import ResvReservationOption
from app.features.reserve.schemas.cast.cast_edit_schema import CustomOption


from app.db.models.station import Station

def update_reservation(db: Session, reservation_data: dict):
    """予約情報を更新する

    Args:
        db (Session): DBセッション
        reservation_data (dict): 予約データ
            - reservation_id: 予約ID
            - cast_id: キャストID
            - course_id: コースID
            - start_time: 開始時間
            - end_time: 終了時間
            - location: 場所
            - reservation_note: 予約メモ
            - status: ステータス
            - transportation_fee: 交通費

    Returns:
        ResvReservation: 更新された予約情報
    """
    try:
        reservation = db.query(ResvReservation).filter(ResvReservation.id == reservation_data["reservation_id"]).first()

        if not reservation:
            raise ValueError(f"Reservation not found: {reservation_data['reservation_id']}")
        
        # 予約情報を更新
        reservation.cast_id = reservation_data["cast_id"]
        reservation.course_id = reservation_data["course_id"]  # コースIDを更新
        reservation.start_time = reservation_data["start_time"]
        reservation.end_time = reservation_data["end_time"]
        reservation.location = reservation_data["location"]
        reservation.reservation_note = reservation_data["reservation_note"]
        reservation.status = reservation_data["status"]
        
        # 交通費を更新
        if "transportation_fee" in reservation_data:
            print(f"DEBUG - [リポジトリ層] 交通費を更新: {reservation_data['transportation_fee']}")
            reservation.traffic_fee = reservation_data["transportation_fee"]
            print(f"DEBUG - [リポジトリ層] 更新後の交通費: {reservation.traffic_fee}")
        
        # locationの処理
        # 1. 数値のみ（駅ID）の場合
        if reservation.location and reservation.location.strip().isdigit():
            # 駅IDとして取り扱い
            reservation.location = reservation.location.strip()
            # 駅に関連する緯度経度を設定
            try:
                station = db.query(Station).filter(Station.id == int(reservation.location.strip())).first()
                if station and station.lat and station.lon:
                    reservation.latitude = station.lat
                    reservation.longitude = station.lon
            except Exception as e:
                print(f"DEBUG - 駅情報取得エラー: {e}")
        # 2. 「緯度,経度」フォーマットの場合
        else:
            try:
                parts = reservation.location.split(',')
                if len(parts) == 2:
                    latitude, longitude = parts
                    reservation.latitude = float(latitude.strip())
                    reservation.longitude = float(longitude.strip())
            except (ValueError, AttributeError) as e:
                print(f"DEBUG - 位置情報解析エラー: {e}")
                # フォーマットが不正な場合は位置情報更新をスキップ
                pass
        
        db.commit()
        db.refresh(reservation)
        
        return reservation
    except Exception as e:
        db.rollback()
        raise e


def add_status_history(
    db: Session,
    reservation_id: int,
    prev_status: str,
    new_status: str = "waiting_user_confirm",
    changed_by: str = "cast"
) -> ResvStatusHistory:
    """ステータス履歴を追加する"""
    
    status_history = ResvStatusHistory(
        reservation_id=reservation_id,
        changed_by=changed_by,
        prev_status=prev_status,
        new_status=new_status,
        status_time=datetime.now()
    )
    
    db.add(status_history)
    db.commit()
    db.refresh(status_history)
    return status_history


from app.db.models.point_details import PointDetailsOption

def update_reservation_options(
    db: Session,
    reservation_id: int,
    option_ids: List[int],
    custom_options: List[CustomOption]
) -> bool:
    """予約オプションを全て入れ替える"""
    
    print(f"DEBUG - [リポジトリ層] オプション更新開始: 予約ID={reservation_id}")
    print(f"DEBUG - [リポジトリ層] 選択オプション: {option_ids}")
    print(f"DEBUG - [リポジトリ層] カスタムオプション数: {len(custom_options)}個")
    
    try:
        # リクエスト内容をDBログに残す（デバッグ用）
        print(f"DEBUG - [リポジトリ層] カスタムオプション内容:")
        for i, opt in enumerate(custom_options):
            print(f"  #{i+1}: name={opt.name}, price={opt.price}")
    
        # 既存のオプションをすべて物理削除（完全に削除して再作成する方式に変更）
        db.query(ResvReservationOption).filter(
            ResvReservationOption.reservation_id == reservation_id
        ).delete(synchronize_session=False)
        
        print(f"DEBUG - [リポジトリ層] 既存オプションをすべて物理削除済み")
        
        # マスターオプションを登録
        for option_id in option_ids:
            # マスターからオプション情報を取得
            master_option = db.query(PointDetailsOption).filter(
                PointDetailsOption.id == option_id
            ).first()
            
            option_price = 0
            if master_option:
                option_price = master_option.price
                print(f"DEBUG - [リポジトリ層] マスターオプション取得: ID={option_id}, 価格={option_price}")
            else:
                print(f"DEBUG - [リポジトリ層] マスターオプション未取得: ID={option_id}")
            
            # 新規オプションとして追加
            print(f"DEBUG - [リポジトリ層] オプション追加: ID={option_id}, 価格={option_price}")
            option = ResvReservationOption(
                reservation_id=reservation_id,
                option_id=option_id,
                option_price=option_price,
                custom_name=None,
                status="active"
            )
            db.add(option)
        
        # カスタムオプションを登録（一意の名前をチェックして重複防止）
        custom_option_names = set()  # 登録済み名前を追跡
        
        for i, custom in enumerate(custom_options):
            # 同じ名前のカスタムオプションがすでに処理されていれば、重複としてスキップ
            if custom.name in custom_option_names:
                print(f"DEBUG - [リポジトリ層] カスタムオプション重複スキップ: 名前={custom.name}")
                continue
                
            # 名前を追跡リストに追加
            custom_option_names.add(custom.name)
            
            print(f"DEBUG - [リポジトリ層] カスタムオプション追加 #{i+1}: 名前={custom.name}, 価格={custom.price}")
            option = ResvReservationOption(
                reservation_id=reservation_id,
                option_id=0,  # カスタムオプションの場合は0を設定
                option_price=custom.price,
                custom_name=custom.name,
                status="active"
            )
            db.add(option)
        
        # 最終的な状態を確認
        all_options = db.query(ResvReservationOption).filter(
            ResvReservationOption.reservation_id == reservation_id
        ).all()
        
        print(f"DEBUG - [リポジトリ層] オプション更新後の総数: {len(all_options)}個")
        print(f"DEBUG - [リポジトリ層] アクティブなオプション数: {len([o for o in all_options if o.status == 'active'])}個")
        print(f"DEBUG - [リポジトリ層] カスタムオプション数: {len([o for o in all_options if o.status == 'active' and o.option_id == 0])}個")
        
        # コミット
        db.commit()
        print(f"DEBUG - [リポジトリ層] オプション更新完了: コミット成功")
        return True
    except Exception as e:
        print(f"ERROR - [リポジトリ層] オプション更新中にエラー発生: {str(e)}")
        db.rollback()
        return False


def verify_reservation_ownership(
    db: Session, 
    reservation_id: int, 
    cast_id: int
) -> bool:
    """予約オーナーシップ確認（他人の予約を編集できないようにする）"""
    
    reservation = db.query(ResvReservation).filter(
        ResvReservation.id == reservation_id,
        ResvReservation.cast_id == cast_id
    ).first()
    
    return reservation is not None
