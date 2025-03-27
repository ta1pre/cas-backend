from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os

# ✅ Bearerトークンのスキーム
security = HTTPBearer()

# ✅ 環境変数から秘密鍵を取得
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # 本番環境では.envで管理

def verify_access_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    ✅ トークンを検証してユーザー情報を返す
    """
    token = credentials.credentials
    try:
        # ✅ トークンのデコード（HS256アルゴリズム）
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: user_id missing")

        return {"user_id": user_id}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
