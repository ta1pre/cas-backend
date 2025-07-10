from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.features.points.schemas.points_schema import PointBalanceResponse, PointHistoryRequest, PointHistoryResponse, ApplyPointRuleRequest, ApplyPointRuleResponse, ReferredUserResponse # ReferredUserResponseを追加
from typing import List, Optional
from app.features.points.services.points_service import fetch_point_balance, fetch_point_history, get_referred_users_list # get_referred_users_listを追加
from app.features.points.services.apply_point_rule_service import apply_point_rule
from app.core.security import get_current_user
from app.db.models.user import User # Userモデルをインポート

router = APIRouter()

@router.post("/balance", response_model=PointBalanceResponse)
def get_point_balance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return fetch_point_balance(db, current_user.id)

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
    - 「rule_name」 に一致するルールをDBから取得し、適用
    - 可変パラメータ（変数ありの場合）は `data.variables` に渡す
    """
    result = apply_point_rule(db, data.user_id, data.rule_name, data.variables)
    if not result:
        raise HTTPException(status_code=400, detail="ルール適用に失敗しました")
    return result

@router.post("/referred_users", response_model=List[ReferredUserResponse])
def get_referred_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    認証済みユーザーが紹介したユーザー（被紹介者）の一覧を取得する
    """
    referred_users = get_referred_users_list(db, current_user.id)
    return referred_users

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
