# テナント作成エンドポイント雛形
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.db.models.user import User
from app.features.admin.tenant.schemas.tenant_create import TenantCreateRequest, TenantCreateResponse
from app.core.security import get_password_hash
import uuid
import traceback        

router = APIRouter()

@router.post("", response_model=TenantCreateResponse)
def create_tenant(
    req: TenantCreateRequest,
    db: Session = Depends(get_db)
):
    # メール重複チェック
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="メールアドレスは既に登録されています")
    
    try:
        # line_id の生成 - 必ず有効な値にする
        generated_line_id = f"tenant_{uuid.uuid4().hex[:16]}"
        print(f"[DEBUG] Generated tenant line_id: {generated_line_id}")
        
        # 手動でSQLクエリを実行して確実にline_idを含める
        # SQLAlchemyのORM方式ではなく、直接SQLを使用
        result = db.execute(
            text("""
            INSERT INTO users 
            (email, password_hash, nick_name, user_type, setup_status, line_id) 
            VALUES (:email, :password_hash, :nick_name, :user_type, :setup_status, :line_id)
            """),
            {
                "email": req.email,
                "password_hash": get_password_hash(req.password),
                "nick_name": req.nick_name,
                "user_type": "tenant",
                "setup_status": "completed",
                "line_id": generated_line_id
            }
        )
        db.commit()
        
        # 作成されたユーザーを取得
        user = db.query(User).filter(User.line_id == generated_line_id).first()
        if not user:
            raise Exception("ユーザー作成後の取得に失敗しました")
            
        print(f"[DEBUG] Successfully created tenant with line_id: {user.line_id}, id: {user.id}")
        return TenantCreateResponse(user_id=user.id, email=user.email, status="success")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to create tenant: {str(e)}")
        print(traceback.format_exc())  # 詳細なエラースタックトレースを出力
        raise HTTPException(status_code=500, detail=f"テナント登録に失敗しました: {str(e)}")
