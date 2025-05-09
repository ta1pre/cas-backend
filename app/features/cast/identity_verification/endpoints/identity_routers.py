from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.session import get_db
from app.core.security import get_current_user
from app.features.cast.identity_verification.schemas.identity_schema import (
    IdentityVerificationRequest,
    IdentityVerificationResponse,
    ReviewVerificationRequest,
    IdentityDocumentsResponse,
    BankAccountUpdateRequest
)
from app.features.cast.identity_verification.services.identity_service import (
    create_verification_request,
    get_verification_status,
    review_verification,
    get_verification_documents,
    update_bank_account
)

# 認証が必要なルーター
identity_router = APIRouter(
    dependencies=[Depends(get_current_user)],
    tags=["Identity Verification"]
)

# 本人確認申請エンドポイント
@identity_router.post("/submit", response_model=IdentityVerificationResponse)
def submit_verification(
    request: IdentityVerificationRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    本人確認申請を提出する
    - サービスタイプと必要な書類をチェック
    - 申請ステータスを「審査中」に更新
    """
    # デバッグ情報を出力
    print(f"リクエスト受信: user_id={user_id}, request={request}")
    
    # キャストIDを使用
    cast_id = request.cast_id if request.cast_id is not None else user_id
    print(f"使用するcast_id: {cast_id}")
    
    # サービスタイプと必要な書類
    if request.service_type == "B" and not request.juminhyo_media_id:
        raise HTTPException(
            status_code=400,
            detail="風俗関連サービスの場合、住民票書類は必須です"
        )
    
    # 身分証明書類
    if not request.id_photo_media_id:
        raise HTTPException(
            status_code=400,
            detail="身分証明書類は必須です"
        )
    
    # 本人確認申請を作成
    try:
        result = create_verification_request(
            cast_id, 
            request.service_type, 
            request.id_photo_media_id, 
            request.juminhyo_media_id,
            request.bank_name,
            request.branch_name,
            request.branch_code,
            request.account_type,
            request.account_number,
            request.account_holder,
            db
        )
        print(f"申請作成結果: {result}")
        return result
    except Exception as e:
        print(f"エラー発生: {str(e)}")
        raise

# 口座情報のみを更新するエンドポイント
@identity_router.post("/update-bank-account", response_model=IdentityVerificationResponse)
def update_bank_account_endpoint(
    request: BankAccountUpdateRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    口座情報のみを更新する
    - 身分証明書や住民票は不要
    - 既存レコードがあれば更新、なければ新規作成
    """
    # デバッグ情報を出力
    print(f"口座情報更新リクエスト受信: user_id={user_id}, request={request}")
    
    # キャストIDを使用
    cast_id = request.cast_id if request.cast_id is not None else user_id
    print(f"使用するcast_id: {cast_id}")
    
    # 口座情報を更新
    try:
        result = update_bank_account(
            cast_id,
            request.bank_name,
            request.branch_name,
            request.branch_code,
            request.account_type,
            request.account_number,
            request.account_holder,
            db
        )
        print(f"口座情報更新結果: {result}")
        return result
    except Exception as e:
        print(f"エラー発生: {str(e)}")
        raise

# 本人確認ステータス確認エンドポイント（GET/POSTの両方をサポート）
@identity_router.get("/status")
@identity_router.post("/status")
def check_verification_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    本人確認ステータス取得（レスポンスモデル一時無効）
    """
    result = get_verification_status(current_user.id, db)
    print(f"[ROUTER DEBUG] Returning result: {result}")  # レスポンス確認用
    return result

# 本人確認書類一覧取得エンドポイント（GET/POSTの両方をサポート）
@identity_router.get("/documents", response_model=IdentityDocumentsResponse)
@identity_router.post("/documents", response_model=IdentityDocumentsResponse)
def get_documents(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    アップロードされた本人確認書類の一覧を取得する
    GET/POSTの両方をサポート
    """
    documents = get_verification_documents(user_id, db)
    return {"documents": documents}

# 管理者用：本人確認審査エンドポイント
@identity_router.post("/review", response_model=IdentityVerificationResponse)
def review_verification_request(
    request: ReviewVerificationRequest,
    db: Session = Depends(get_db),
    admin_id: int = Depends(get_current_user)  # TODO: 管理者権限チェックを追加
):
    """
    管理者が本人確認申請を審査する
    - ステータスを「承認」または「却下」に更新
    - 却下の場合は理由を記録
    """
    # TODO: 管理者権限のチェックを追加
    
    return review_verification(
        request.cast_id,
        request.status,
        admin_id,  # 審査者ID
        request.rejection_reason,
        db
    )
