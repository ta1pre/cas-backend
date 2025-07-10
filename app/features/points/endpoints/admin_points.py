from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.features.points.repositories import points_repository
from app.features.points.schemas.admin_points_schema import (
    PointRuleResponse,
    PointRuleUpdateRequest
)
from typing import List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/rules", response_model=List[PointRuleResponse])
async def get_point_rules(db: Session = Depends(get_db)):
    """
    ポイントルール一覧を取得（管理画面用）
    """
    try:
        logger.info("🔍 [admin] ポイントルール一覧取得開始")
        
        rules = points_repository.get_all_point_rules(db)
        
        if not rules:
            logger.info("⚠️ [admin] ポイントルールが見つかりません")
            return []
        
        logger.info(f"✅ [admin] ポイントルール一覧取得成功: {len(rules)}件")
        return rules
        
    except Exception as e:
        logger.error(f"❌ [admin] ポイントルール一覧取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail="ポイントルール一覧の取得に失敗しました")

@router.put("/rules/{rule_id}")
async def update_point_rule(
    rule_id: int,
    rule_data: PointRuleUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    ポイントルールを更新（管理画面用）
    """
    try:
        logger.info(f"🔧 [admin] ポイントルール更新開始: rule_id={rule_id}")
        
        # ルールの存在確認
        existing_rule = points_repository.get_point_rule_by_id(db, rule_id)
        if not existing_rule:
            logger.warning(f"⚠️ [admin] ルールが見つかりません: rule_id={rule_id}")
            raise HTTPException(status_code=404, detail="指定されたルールが見つかりません")
        
        # ルール更新
        updated_rule = points_repository.update_point_rule(db, rule_id, rule_data.dict(exclude_unset=True))
        
        logger.info(f"✅ [admin] ポイントルール更新成功: rule_id={rule_id}")
        return {"message": "ポイントルールが正常に更新されました", "rule": updated_rule}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [admin] ポイントルール更新エラー: rule_id={rule_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail="ポイントルールの更新に失敗しました")

@router.patch("/rules/{rule_id}/toggle")
async def toggle_point_rule_status(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """
    ポイントルールの有効/無効を切り替え（管理画面用）
    """
    try:
        logger.info(f"🔄 [admin] ポイントルール状態切り替え開始: rule_id={rule_id}")
        
        # ルールの存在確認
        existing_rule = points_repository.get_point_rule_by_id(db, rule_id)
        if not existing_rule:
            logger.warning(f"⚠️ [admin] ルールが見つかりません: rule_id={rule_id}")
            raise HTTPException(status_code=404, detail="指定されたルールが見つかりません")
        
        # ステータス切り替え（is_activeフィールドがあると仮定）
        # 実際のテーブル構造に応じて調整が必要
        new_status = not getattr(existing_rule, 'is_active', True)
        updated_rule = points_repository.update_point_rule(db, rule_id, {"is_active": new_status})
        
        status_text = "有効" if new_status else "無効"
        logger.info(f"✅ [admin] ポイントルール状態切り替え成功: rule_id={rule_id}, status={status_text}")
        
        return {
            "message": f"ポイントルールを{status_text}に変更しました",
            "rule_id": rule_id,
            "is_active": new_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [admin] ポイントルール状態切り替えエラー: rule_id={rule_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail="ポイントルールの状態切り替えに失敗しました")