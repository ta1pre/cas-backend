from sqlalchemy.orm import Session
from sqlalchemy import asc
from app.db.models.cast_servicetype import CastServiceType, CastServiceTypeList  
from app.db.models.cast_common_prof import CastCommonProf
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class ServiceTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_service_types(self):
        """
        ✅ `cast_servicetype_list`（サービスタイプリスト）の全データを取得（weight順）
        """
        logger.info("【service type list】サービスタイプリストのデータ取得開始")

        service_types = (
            self.db.query(CastServiceTypeList)
            .order_by(asc(CastServiceTypeList.weight))
            .all()
        )

        logger.info(f"【service type list】取得データ: {service_types}")

        return service_types

    def get_selected_service_types(self, cast_id: int) -> list[int]:
        """
        ✅ 指定したキャストの現在のサービスタイプ ID リストを取得
        """
        selected_services = (
            self.db.query(CastServiceType.servicetype_id)
            .filter(CastServiceType.cast_id == cast_id)
            .all()
        )

        return [service.servicetype_id for service in selected_services]

    def register_service_types(self, cast_id: int, servicetype_ids: list[int]):
        """
        ✅ キャストのサービスタイプをまとめて登録
        """
        logger.info(f"【service type register】キャストID: {cast_id} | 登録するサービスタイプID: {servicetype_ids}")

        # キャストプロフィールの存在を確認
        cast_profile = self.db.query(CastCommonProf).filter(CastCommonProf.cast_id == cast_id).first()
        if not cast_profile:
            logger.error(f"【service type register】エラー: キャストID {cast_id} のプロフィールが存在しません")
            raise HTTPException(status_code=400, detail=f"キャストID {cast_id} のプロフィールが存在しません。先にキャスト登録を完了してください")

        new_services = [CastServiceType(cast_id=cast_id, servicetype_id=servicetype_id) for servicetype_id in servicetype_ids]
        logger.info(f"【service type register】登録データ: {new_services}")

        self.db.add_all(new_services)
        self.db.flush()  # 追加
        self.db.commit()

        logger.info(f"【service type register】サービスタイプを登録しました: {servicetype_ids}")



    def delete_service_types(self, cast_id: int, service_type_ids: list[int]):
        """
        ✅ キャストのサービスタイプをまとめて削除
        """
        logger.info(f"【service type delete】キャストID: {cast_id} | 削除するサービスタイプID: {service_type_ids}")

        self.db.query(CastServiceType).filter(
            CastServiceType.cast_id == cast_id, CastServiceType.servicetype_id.in_(service_type_ids)
        ).delete(synchronize_session=False)
        self.db.commit()

        logger.info(f"【service type delete】サービスタイプを削除しました: {service_type_ids}")
