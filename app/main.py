from fastapi import FastAPI
from app.api.v1.routers.master_router import master_router  # 直接指定
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.config import FRONTEND_URL  # 追加


logging.basicConfig(
    level=logging.DEBUG,  # DEBUG レベルのログを出力するように変更
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",  # モジュール名も表示
    handlers=[
        logging.StreamHandler()  # ターミナルに出力
    ]
)

# 特定のモジュールのログレベルを設定
logger = logging.getLogger(__name__)
logging.getLogger("webhook").setLevel(logging.DEBUG)
logging.getLogger("line_client").setLevel(logging.DEBUG)
logging.getLogger("faq_search").setLevel(logging.DEBUG)


app = FastAPI()

# API全体のルーターを1行で登録
app.include_router(master_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"msg": "Hello from local!"}

origins = [
    FRONTEND_URL,
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # `*` ではなく、特定のドメインを指定
    allow_credentials=True,  # `withCredentials: true` を許可
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)