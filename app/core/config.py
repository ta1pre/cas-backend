import os
from dotenv import load_dotenv

# `.env` を明示的に指定してロード
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
if os.path.exists(dotenv_path):
    print(f"✅ `.env` をロード: {dotenv_path}")
    load_dotenv(dotenv_path, override=True)  # ← `override=True` を必ず設定
else:
    print("💡 `.env` が見つかりません。環境変数から直接読み込みます。")

#データベース
DATABASE_URL = os.getenv("DATABASE_URL")

# `REDIRECT_URI` の値を出力
REDIRECT_URI = os.getenv("REDIRECT_URI")
print(f"DEBUG: REDIRECT_URI (os.getenv) = {REDIRECT_URI}")

# `os.environ.get` を使っても確認
print(f"DEBUG: REDIRECT_URI (os.environ) = {os.environ.get('REDIRECT_URI')}")

# LINE API関連
LINE_LOGIN_CHANNEL_ID = os.getenv("LINE_LOGIN_CHANNEL_ID")
LINE_LOGIN_CHANNEL_SECRET = os.getenv("LINE_LOGIN_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# ✅ `TEST_VARIABLE` を読み込む
TEST_VARIABLE = os.getenv("TEST_VARIABLE")
print(f"DEBUG: TEST_VARIABLE = {TEST_VARIABLE}")
print(f"DEBUG: REDIRECT_URI = {REDIRECT_URI}")  # ここで値を確認


# フロントエンドURL
FRONTEND_URL = os.getenv("FRONTEND_URL")

# JWT関連
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "your_refresh_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS",60))
# OpenAI API関連
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# microCMS
MICROCMS_API_URL= os.getenv("MICROCMS_API_URL")
MICROCMS_API_KEY= os.getenv("MICROCMS_API_KEY")
