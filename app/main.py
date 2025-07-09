from fastapi import FastAPI
from app.api.v1.routers.master_router import master_router  # 直接指定
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import sys
from app.core.config import FRONTEND_URL  # 追加
from fastapi import Request

# AWS環境かどうかを判定
is_aws = os.getenv("AWS_EXECUTION_ENV") is not None or os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None

# ログレベル
log_level = logging.DEBUG if not is_aws else logging.INFO

logging.basicConfig(
    level=log_level,  
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",  
    handlers=[
        logging.StreamHandler()  
    ]
)

# ロガー
logger = logging.getLogger(__name__)

# ログレベル設定
if is_aws:
    logger.info("AWS環境で動作中、ログレベルを設定します")
    # AWS環境でログレベルを調整
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    
    # LINE関連のログレベルを調整
    logging.getLogger("webhook").setLevel(logging.INFO)
    logging.getLogger("line_client").setLevel(logging.INFO)
    logging.getLogger("faq_search").setLevel(logging.INFO)
    logging.getLogger("config").setLevel(logging.INFO)
    
    # 例外処理
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Ctrl+Cなどによる終了はデフォルトの処理を実行
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    # 例外処理を設定
    sys.excepthook = handle_exception
    
    logger.info("AWS環境用のログレベル設定を完了しました")
else:
    logger.info("ローカル環境で動作中、デバッグログを有効にします")
    # ローカル環境でデバッグログを有効にする
    logging.getLogger("webhook").setLevel(logging.DEBUG)
    logging.getLogger("line_client").setLevel(logging.DEBUG)
    logging.getLogger("faq_search").setLevel(logging.DEBUG)
    logging.getLogger("config").setLevel(logging.DEBUG)


app = FastAPI()

# API全体のルーターを1行で登録
app.include_router(master_router, prefix="/api/v1")

@app.get("/")
def root():
    if is_aws:
        return {"msg": "Hello from AWS production!", "env": "production"}
    else:
        return {"msg": "Hello from local!", "env": "development"}

origins = [
    FRONTEND_URL,
    "https://cas.tokyo",
    "http://localhost:3000",  # ローカル開発用
    "http://localhost:3001",  # Next.jsがポート変更した場合
]

# AWS環境の場合は本番用のoriginsのみ使用
if is_aws:
    origins = [
        "https://cas.tokyo",
        "https://www.cas.tokyo",  # www付きも許可
    ]
    logger.info(f"AWS環境でCORS設定: {origins}")
else:
    logger.info(f"ローカル環境でCORS設定: {origins}")

# Webhook用のミドルウェア設定（CORSを無効化）
class WebhookMiddleware:
    async def __call__(self, request: Request, call_next):
        if request.url.path == "/api/v1/payments/webhook":
            # Webhookエンドポイントの場合、特別な処理を行う
            response = await call_next(request)
            return response
        else:
            # 通常のエンドポイントの場合、標準の処理を行う
            return await call_next(request)

# カスタムミドルウェアを追加（CORSミドルウェアの前に）
app.middleware("http")(WebhookMiddleware())

# CORSミドルウェアを追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # `*` ではなく、特定のドメインを指定
    allow_credentials=True,  # `withCredentials: true` を許可
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)

# アプリケーション起動完了ログ
logger.info(f"Application startup complete. Running in {'AWS' if is_aws else 'local'} environment.")