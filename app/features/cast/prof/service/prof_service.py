# Cast Profile Service
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..repository import prof_repository
from ..schema import prof_schema
from app.db.models.cast_common_prof import CastCommonProf # For type hinting
# 絶対パスでインポートに変更（同一ファイルからのインポートを避ける）
from app.features.customer.area.service.station_service import get_nearest_stations
from app.db.models.station import Station
from typing import Dict, Any
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
