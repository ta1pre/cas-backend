from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import func

from app.db.models.resv_reservation import ResvReservation
from app.db.models.resv_status_history import ResvStatusHistory
from app.db.models.resv_reservation_option import ResvReservationOption
from app.features.reserve.schemas.cast.cast_edit_schema import CustomOption
from app.features.reserve.repositories.common.price_calculator import calculate_reservation_points

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

    Returns:
        ResvReservation: 更新された予約情報
    """
    try:
        reservation = db.query(ResvReservation).filter(ResvReservation.id == reservation_data["reservation_id"]).first()

        if not reservation:
            raise ValueError(f"Reservation not found: {reservation_data['reservation_id']}")
        
        # 予約情報を更新
        print(f"DEBUG - [リポジトリ層] 予約更新開始: reservation_id={reservation_data['reservation_id']}")
        print(f"DEBUG - [リポジトリ層] 更新内容: {reservation_data}")
        
        reservation.cast_id = reservation_data["cast_id"]
        print(f"DEBUG - [リポジトリ層] cast_idを更新: {reservation.cast_id}")
        
        reservation.course_id = reservation_data["course_id"]  # コースIDを更新
        print(f"DEBUG - [リポジトリ層] course_idを更新: {reservation.course_id}")
        
        # start_timeの処理
        if isinstance(reservation_data["start_time"], str):
            # YYYY-MM-DD HH:MM:SS 形式の文字列をdatetimeに変換
            # これは日本時間として解釈される
            try:
                start_time_local = datetime.strptime(reservation_data["start_time"], '%Y-%m-%d %H:%M:%S')
                print(f"DEBUG - [リポジトリ層] 受信したローカル時間文字列 start_time: {reservation_data['start_time']}")
                print(f"DEBUG - [リポジトリ層] パースされたローカル start_time: {start_time_local}")
                reservation.start_time = start_time_local
            except ValueError as e:
                print(f"ERROR - [リポジトリ層] start_timeのパースに失敗: {e}")
                # エラー処理: 必要に応じてデフォルト値設定や例外送出を行う
                raise ValueError(f"Invalid start_time format: {reservation_data['start_time']}") from e
        else:
            # すでにdatetimeオブジェクトの場合はそのまま使用 (通常はこのパスは通らないはず)
            reservation.start_time = reservation_data["start_time"]
            print(f"DEBUG - [リポジトリ層] datetimeオブジェクトのstart_time: {reservation.start_time}")
            
        print(f"DEBUG - [リポジトリ層] start_timeを更新 (DB保存用): {reservation.start_time}")
        
        # end_timeの処理
        if "end_time" in reservation_data and reservation_data["end_time"]:
            if isinstance(reservation_data["end_time"], str):
                # YYYY-MM-DD HH:MM:SS 形式の文字列をdatetimeに変換
                try:
                    end_time_local = datetime.strptime(reservation_data["end_time"], '%Y-%m-%d %H:%M:%S')
                    print(f"DEBUG - [リポジトリ層] 受信したローカル時間文字列 end_time: {reservation_data['end_time']}")
                    print(f"DEBUG - [リポジトリ層] パースされたローカル end_time: {end_time_local}")
                    reservation.end_time = end_time_local
                except ValueError as e:
                    print(f"ERROR - [リポジトリ層] end_timeのパースに失敗: {e}")
                    raise ValueError(f"Invalid end_time format: {reservation_data['end_time']}") from e
            else:
                # すでにdatetimeオブジェクトの場合はそのまま使用
                reservation.end_time = reservation_data["end_time"]
                print(f"DEBUG - [リポジトリ層] datetimeオブジェクトのend_time: {reservation.end_time}")
                
            print(f"DEBUG - [リポジトリ層] end_timeを更新 (DB保存用): {reservation.end_time}")
            # end_timeが指定されている場合は、後で計算したend_timeを使用しない
            use_specified_end_time = True
        else:
            use_specified_end_time = False
            
        reservation.location = reservation_data["location"]
        reservation.reservation_note = reservation_data["reservation_note"]
        reservation.status = reservation_data["status"]
        
        # 交通費を更新
        traffic_fee = 0
        if "transportation_fee" in reservation_data:
            traffic_fee = reservation_data["transportation_fee"]
            reservation.traffic_fee = traffic_fee
        
        # オプションの合計を計算
        # サービス層から渡されたoption_pointsがあればそれを使用し、なければDBから計算する
        if "option_points" in reservation_data and reservation_data["option_points"] is not None:
            option_points = reservation_data["option_points"]
            print(f"DEBUG - [リポジトリ層] サービス層から渡されたoption_points: {option_points}")
        else:
            option_points = db.query(func.sum(ResvReservationOption.option_price)).filter(
                ResvReservationOption.reservation_id == reservation_data["reservation_id"],
                ResvReservationOption.status == "active"
            ).scalar() or 0
            print(f"DEBUG - [リポジトリ層] DBから計算したoption_points: {option_points}")
        
        # 料金計算
        points_data = calculate_reservation_points(
            db, 
            reservation.course_id, 
            reservation.cast_id, 
            option_points, 
            traffic_fee
        )
        
        # 料金情報を更新
        reservation.course_points = points_data['course_points']
        reservation.option_points = option_points
        reservation.reservation_fee = points_data['reservation_fee']
        reservation.total_points = points_data['total_points']
        reservation.cast_reward_points = points_data['cast_reward_points']
        
        # end_timeを指定されなかった場合、計算したend_timeを使用
        if not use_specified_end_time:
            reservation.end_time = reservation.start_time + points_data['end_time_delta']
            print(f"DEBUG - end_timeを計算した場合: {reservation.end_time}")
        else:
            print(f"DEBUG - 指定されたend_timeを使用: {reservation.end_time}")
        
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
        
        # デバッグ
        print(f"DEBUG - [リポジトリ層] 更新処理の最終段階")
        print(f"DEBUG - [リポジトリ層] 更新後のデータ: start_time={reservation.start_time}, end_time={reservation.end_time}")
        print(f"DEBUG - [リポジトリ層] 更新後のoption_points: {reservation.option_points}")
        
        # リポジトリ層ではコミットせず、データの更新のみを行う
        # サービス層でコミットを行うため、ここではコミットしない
        print(f"DEBUG - [リポジトリ層] 予約データ更新完了（コミットはサービス層で実行）: reservation_id={reservation_data['reservation_id']}")
        
        return reservation
    except Exception as e:
        print(f"ERROR - [リポジトリ層] 予約更新エラー: {str(e)}")
        # ロールバックもサービス層で行うため、ここではロールバックしない
        print(f"ERROR - [リポジトリ層] エラー発生（ロールバックはサービス層で実行）")
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
            
            # 価格を確実に数値型に変換
            try:
                option_price = int(custom.price)
            except (ValueError, TypeError):
                print(f"ERROR - [リポジトリ層] カスタムオプション価格変換エラー: 名前={custom.name}, 価格={custom.price}, 型={type(custom.price)}")
                option_price = 0  # デフォルト値を設定
            
            print(f"DEBUG - [リポジトリ層] カスタムオプション追加 #{i+1}: 名前={custom.name}, 価格={option_price} (変換後)")
            option = ResvReservationOption(
                reservation_id=reservation_id,
                option_id=0,  # カスタムオプションの場合は0を設定
                option_price=option_price,  # 変換後の価格を使用
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
        
        # コミットはサービス層で行うため、ここではコミットしない
        print(f"DEBUG - [リポジトリ層] オプション更新完了（コミットはサービス層で実行）: 予約ID={reservation_id}")
        
        # 予約情報を取得
        reservation = db.query(ResvReservation).filter(ResvReservation.id == reservation_id).first()
        if not reservation:
            print(f"ERROR - [リポジトリ層] 予約情報取得エラー: ID={reservation_id}")
            return False
        
        # オプションの合計を計算
        option_points = db.query(func.sum(ResvReservationOption.option_price)).filter(
            ResvReservationOption.reservation_id == reservation_id,
            ResvReservationOption.status == "active"
        ).scalar() or 0
        
        # 交通費を取得
        traffic_fee = reservation.traffic_fee or 0
        
        # 料金計算
        points_data = calculate_reservation_points(
            db, 
            reservation.course_id, 
            reservation.cast_id, 
            option_points, 
            traffic_fee
        )
        
        # 料金情報を更新
        reservation.course_points = points_data['course_points']
        reservation.option_points = option_points
        reservation.total_points = points_data['total_points']
        reservation.cast_reward_points = points_data['cast_reward_points']
        
        # コミットはサービス層で行うため、ここではコミットしない
        print(f"DEBUG - [リポジトリ層] オプション更新後の料金計算結果: total_points={points_data['total_points']}")
        print(f"DEBUG - [リポジトリ層] オプション更新完了: コミットはサービス層で実行")
        return True
    except Exception as e:
        print(f"ERROR - [リポジトリ層] オプション更新中にエラー発生: {str(e)}")
        # ロールバックもサービス層で行うため、ここではロールバックしない
        print(f"ERROR - [リポジトリ層] エラー発生（ロールバックはサービス層で実行）")
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
