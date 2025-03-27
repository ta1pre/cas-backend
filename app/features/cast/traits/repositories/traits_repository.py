from sqlalchemy.orm import Session
from sqlalchemy import asc
from app.db.models.cast_traits import CastTrait, CastTraitList  
import logging

logger = logging.getLogger(__name__)


class TraitsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_traits(self):
        """
        ✅ `cast_traits_list`（特徴リスト）の全データを取得（weight順）
        """
        logger.info("【traits list】特徴リストのデータ取得開始")

        traits = (
            self.db.query(CastTraitList)
            .order_by(asc(CastTraitList.weight))
            .all()
        )

        logger.info(f"【traits list】取得データ: {traits}")

        return traits

    def get_selected_traits(self, cast_id: int) -> list[int]:
        """
        ✅ 指定したキャストの現在の特徴 ID リストを取得
        """
        selected_traits = (
            self.db.query(CastTrait.trait_id)
            .filter(CastTrait.cast_id == cast_id)
            .all()
        )

        return [trait.trait_id for trait in selected_traits]

    def register_traits(self, cast_id: int, trait_ids: list[int]):
        """
        ✅ キャストの特徴をまとめて登録
        """
        logger.info(f"【traits register】キャストID: {cast_id} | 登録する特徴ID: {trait_ids}")

        new_traits = [CastTrait(cast_id=cast_id, trait_id=trait_id) for trait_id in trait_ids]
        self.db.add_all(new_traits)
        self.db.commit()

        logger.info(f"【traits register】特徴を登録しました: {trait_ids}")

    def delete_traits(self, cast_id: int, trait_ids: list[int]):
        """
        ✅ キャストの特徴をまとめて削除
        """
        logger.info(f"【traits delete】キャストID: {cast_id} | 削除する特徴ID: {trait_ids}")

        self.db.query(CastTrait).filter(
            CastTrait.cast_id == cast_id, CastTrait.trait_id.in_(trait_ids)
        ).delete(synchronize_session=False)
        self.db.commit()

        logger.info(f"【traits delete】特徴を削除しました: {trait_ids}")
