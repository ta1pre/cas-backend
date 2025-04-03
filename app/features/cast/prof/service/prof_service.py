# Cast Profile Service
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..repository import prof_repository
from ..schema import prof_schema
from app.db.models.cast_common_prof import CastCommonProf # For type hinting
# 絶対パスでインポートに変更（同一ファイルからのインポートを避ける）
from app.features.customer.area.service.station_service import get_nearest_stations
from app.db.models.station import Station
from app.db.models.prefectures import Prefecture
from typing import Dict, Any, List
import logging

# ロガーの設定
logger = logging.getLogger(__name__)

# 駅IDから駅名を取得する関数を直接定義
def get_station_by_id(db: Session, station_id):
    """駅IDから駅情報を取得する"""
    logger.info(f"駅ID検索: {station_id}, 型: {type(station_id)}")
    
    try:
        # 駅IDの処理 - 特殊な形式の場合を考慮
        # 例：1130209のような形式は、エリアコード+駅コードの可能性がある
        # まずそのままの形式で試す
        if station_id and isinstance(station_id, (int, str)):
            station_id_str = str(station_id)
            logger.info(f"駅ID文字列: {station_id_str}")
            
            # 1. そのままのIDで検索
            station = db.query(Station).filter(Station.id == station_id_str).first()
            if station:
                logger.info(f"駅が見つかりました（そのままのID）: {station.name}")
                return station
                
            # 2. 数値変換して検索
            try:
                station_id_int = int(station_id_str)
                station = db.query(Station).filter(Station.id == station_id_int).first()
                if station:
                    logger.info(f"駅が見つかりました（数値変換）: {station.name}")
                    return station
            except ValueError:
                logger.info("数値変換できません")
            
            # 3. 特殊な形式の処理（例：1130209 -> 後ろの部分だけ使う）
            if len(station_id_str) > 4:
                try:
                    # 後ろの部分を抽出して試す（例：1130209 -> 0209）
                    short_id = station_id_str[-4:]
                    station = db.query(Station).filter(Station.id == int(short_id)).first()
                    if station:
                        logger.info(f"駅が見つかりました（短縮ID）: {station.name}")
                        return station
                except Exception as e:
                    logger.error(f"短縮ID検索エラー: {e}")
    except Exception as e:
        logger.error(f"駅検索エラー: {e}")
        
    logger.warning(f"駅が見つかりませんでした: {station_id}")
    return None

# 都道府県IDまたは駅IDから都道府県名を取得する関数を定義
def get_prefecture_names(db: Session, prefecture_ids: str) -> List[str]:
    """都道府県IDまたは駅IDから都道府県名を取得する"""
    logger.info(f"都道府県名取得開始: prefecture_ids={prefecture_ids}")
    if not prefecture_ids:
        logger.info("都道府県IDが空のため、空リストを返します")
        return []
    
    # カンマ区切りの文字列をリストに変換
    try:
        id_list_str = [id_str.strip() for id_str in prefecture_ids.split(',') if id_str.strip()]
        logger.info(f"分割後のID文字列一覧: {id_list_str}")
        
        # 結果を格納するリスト
        result = []
        
        for id_str in id_list_str:
            # 1. まず都道府県IDとして処理を試みる（1〜47の範囲）
            try:
                id_num = int(id_str)
                if 1 <= id_num <= 47:  # 都道府県IDの範囲内
                    prefecture = db.query(Prefecture).filter(Prefecture.id == id_num).first()
                    if prefecture:
                        result.append(prefecture.name)
                        logger.info(f"都道府県ID {id_num} から都道府県名 {prefecture.name} を取得")
                        continue
            except ValueError:
                pass
            
            # 2. 都道府県IDとして見つからない場合は駅IDとして処理
            try:
                # 駅IDとして処理
                station = get_station_by_id(db, id_str)
                if station and station.prefecture_id:
                    # 駅の都道府県IDから都道府県名を取得
                    prefecture = db.query(Prefecture).filter(Prefecture.id == station.prefecture_id).first()
                    if prefecture:
                        result.append(prefecture.name)
                        logger.info(f"駅ID {id_str} から都道府県名 {prefecture.name} を取得")
                        continue
            except Exception as e:
                logger.error(f"駅IDからの都道府県取得エラー: {e}")
        
        logger.info(f"最終的に取得した都道府県名: {result}")
        return result
    except Exception as e:
        logger.error(f"都道府県名取得エラー: {e}")
        return []

def get_profile_service(db: Session, cast_id: int) -> Dict[str, Any]:
    """キャストプロフィール取得サービス"""
    profile = prof_repository.get_cast_prof(db, cast_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cast profile with id {cast_id} not found"
        )
    
    # プロフィール情報をdict形式に変換
    profile_dict = {
        "cast_id": profile.cast_id,
        "rank_id": profile.rank_id,
        "cast_type": profile.cast_type,
        "name": profile.name,
        "age": profile.age,
        "height": profile.height,
        "bust": profile.bust,
        "cup": profile.cup,
        "waist": profile.waist,
        "hip": profile.hip,
        "birthplace": profile.birthplace,
        "blood_type": profile.blood_type,
        "hobby": profile.hobby,
        "reservation_fee": profile.reservation_fee,
        "reservation_fee_deli": profile.reservation_fee_deli,
        "self_introduction": profile.self_introduction,
        "job": profile.job,
        "dispatch_prefecture": profile.dispatch_prefecture,  # そのまま文字列として保持
        "support_area": profile.support_area,
        "popularity": profile.popularity,
        "rating": profile.rating,
        "is_active": profile.is_active,
        "available_at": profile.available_at,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
    }
    
    # support_areaから都道府県名を取得
    logger.info(f"support_area値: {profile.support_area}")
    support_area_names = get_prefecture_names(db, profile.support_area)
    logger.info(f"取得したsupport_area_names: {support_area_names}")
    profile_dict["support_area_names"] = support_area_names
    
    # dispatch_prefectureに関する特別な処理
    # ログを出力するが同じ値を何度も取得しないよう注意
    disp_pref = profile.dispatch_prefecture
    logger.info(f"プロフィール取得: dispatch_prefecture={disp_pref}")
    
    # 駅名・都道府県の処理
    station_name = None
    
    # dispatch_prefectureが数値の形式であれば駅IDとして処理
    if disp_pref and isinstance(disp_pref, str) and disp_pref.isdigit():
        # 駅IDとして処理
        station = get_station_by_id(db, disp_pref)
        if station:
            station_name = station.name
            logger.info(f"駅ID {disp_pref} から駅名 {station_name} を取得しました")
    elif disp_pref:
        # 駅IDでない場合は、そのまま駅名/都道府県名として扱う
        station_name = disp_pref
        logger.info(f"駅名/都道府県名としてそのまま使用: {station_name}")
    
    profile_dict["station_name"] = station_name
    
    # デバッグログ: 返却する辞書の内容と型を出力
    logger.info("--- 返却する profile_dict の内容 ---")
    for key, value in profile_dict.items():
        logger.info(f"{key}: {value} (Type: {type(value)})")
    logger.info("------------------------------------")
    
    # popularityとratingの値をNoneから0または0.0に変更
    if profile_dict["popularity"] is None:
        profile_dict["popularity"] = 0
        logger.info("popularityがNoneだったので0に変更しました")
    
    if profile_dict["rating"] is None:
        profile_dict["rating"] = 0.0
        logger.info("ratingがNoneだったので0.0に変更しました")
    
    # hipフィールドの値をチェックし、不正な値の場合は補正
    if "hip" in profile_dict and profile_dict["hip"] is not None:
        if profile_dict["hip"] < 50 or profile_dict["hip"] > 150:
            logger.warning(f"hipの値({profile_dict['hip']})が不正です。補正します。")
            # バストの値を使用するか、デフォルト値を使用
            if "bust" in profile_dict and profile_dict["bust"] is not None and 50 <= profile_dict["bust"] <= 150:
                profile_dict["hip"] = profile_dict["bust"]
                logger.info(f"hipの値をbustの値({profile_dict['bust']})に変更しました")
            else:
                profile_dict["hip"] = 85  # デフォルト値
                logger.info("hipの値をデフォルト値(85)に変更しました")
    
    # 日付フィールドのNoneチェック
    from datetime import datetime
    current_time = datetime.now()
    
    # available_atがNoneの場合は現在時刻を設定
    if profile_dict.get("available_at") is None:
        profile_dict["available_at"] = current_time
        logger.info("available_atがNoneだったので現在時刻に設定しました")
    
    # created_atがNoneの場合は現在時刻を設定
    if profile_dict.get("created_at") is None:
        profile_dict["created_at"] = current_time
        logger.info("created_atがNoneだったので現在時刻に設定しました")
    
    # reservation_fee_deliの型を明示的に変換 (念のため)
    if "reservation_fee_deli" in profile_dict and profile_dict["reservation_fee_deli"] is not None:
        try:
            profile_dict["reservation_fee_deli"] = int(profile_dict["reservation_fee_deli"])
            logger.info(f"reservation_fee_deli を int に変換しました: {profile_dict['reservation_fee_deli']}")
        except (ValueError, TypeError):
            logger.error(f"reservation_fee_deli を int に変換できませんでした: {profile_dict.get('reservation_fee_deli')}")
            profile_dict["reservation_fee_deli"] = None
    
    return profile_dict

def update_profile_service(db: Session, cast_id: int, prof_data: prof_schema.CastProfUpdate) -> CastCommonProf:
    """キャストプロフィール更新サービス"""
    # 更新前にログ出力
    logger.info(f"プロフィール更新リクエスト: cast_id={cast_id}, data={prof_data.dict()}")
    
    updated_profile = prof_repository.update_cast_prof(db, cast_id, prof_data)
    if not updated_profile:
        # リポジトリで None が返るのは、そもそもキャストが存在しない場合
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cast profile with id {cast_id} not found, cannot update"
        )
    
    # 更新後にログ出力
    logger.info(f"プロフィール更新完了: {updated_profile.cast_id}")
    return updated_profile
