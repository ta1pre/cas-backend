from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.features.points.schemas.points_schema import PointBalanceRequest, PointBalanceResponse, PointHistoryRequest, PointHistoryResponse, ApplyPointRuleRequest, ApplyPointRuleResponse
from app.features.points.services.points_service import fetch_point_balance, fetch_point_balance, fetch_point_history
from app.features.points.services.apply_point_rule_service import apply_point_rule

router = APIRouter()

@router.post("/balance", response_model=PointBalanceResponse)
def get_point_balance(data: PointBalanceRequest, db: Session = Depends(get_db)):
    return fetch_point_balance(db, data.user_id)

@router.post("/history", response_model=PointHistoryResponse)
def get_point_history(data: PointHistoryRequest, db: Session = Depends(get_db)):
    return fetch_point_history(db, data.user_id, data.limit, data.offset)

@router.post("/apply", response_model=ApplyPointRuleResponse)
def apply_point_rule_api(
    data: ApplyPointRuleRequest,
    db: Session = Depends(get_db)
):
    """
    ✅ ルールを適用するAPI
    - `rule_name` に一致するルールをDBから取得し、適用
    - 可変パラメータ（変数ありの場合）は `data.variables` に渡す
    """
    result = apply_point_rule(db, data.user_id, data.rule_name, data.variables)
    if not result:
        raise HTTPException(status_code=400, detail="ルール適用に失敗しました")
    return result

#ポイント購入
from app.features.points.services.purchase_service import process_point_purchase
from app.features.points.schemas.purchase_schema import PurchasePointRequest, PurchasePointResponse

@router.post("/purchase", response_model=PurchasePointResponse)
def purchase_point(request: PurchasePointRequest, db: Session = Depends(get_db)):
    """
    ✅ ユーザーがポイントを購入するAPI
    - `process_point_purchase()` で履歴追加 & 残高更新
    """
    user_id = request.user_id
    amount = request.amount

    try:
        new_balance = process_point_purchase(db, user_id, amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "✅ ポイント購入成功", "new_balance": new_balance.total_point_balance}
