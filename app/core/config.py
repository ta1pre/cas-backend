import os
from dotenv import load_dotenv
import logging
import json
import sys

# ロガーの設定
logger = logging.getLogger("config")

# `.env` を明示的に指定してロード
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
if os.path.exists(dotenv_path):
    print(f"✅ `.env` をロード: {dotenv_path}")
    load_dotenv(dotenv_path, override=True)  # ← `override=True` を必ず設定
else:
    print("💡 `.env` が見つかりません。環境変数から直接読み込みます。")

# AWS環境かどうかを判定
is_aws = os.getenv("AWS_EXECUTION_ENV") is not None or os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None
if is_aws:
    print("\n===== AWS環境で実行中 =====\n")
else:
    print("\n===== ローカル環境で実行中 =====\n")

# データベース
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

# 環境変数の値を確認する関数
def check_env_var(name, value, show_full=False):
    if value:
        if show_full:
            print(f"✅ {name}: {value}")
        else:
            val_length = len(value)
            if val_length > 10:
                masked_val = value[:5] + "*" * (val_length - 10) + value[-5:]
                print(f"✅ {name}: {masked_val} (長さ: {val_length}文字)")
            else:
                print(f"✅ {name}: {'*' * val_length} (長さ: {val_length}文字)")
    else:
        print(f"❌ {name} が設定されていません")

# 必要な環境変数の値を確認
print("\n===== 必要な環境変数の値を確認 =====\n")
check_env_var("LINE_CHANNEL_ACCESS_TOKEN", LINE_CHANNEL_ACCESS_TOKEN)
check_env_var("LINE_CHANNEL_SECRET", LINE_CHANNEL_SECRET)
check_env_var("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
check_env_var("DATABASE_URL", DATABASE_URL, True)
check_env_var("REDIRECT_URI", REDIRECT_URI, True)

# AWS環境の場合、環境変数の値を出力
if is_aws:
    print("\n===== AWS環境で環境変数の値を出力 =====\n")
    print(f"LINE_CHANNEL_ACCESS_TOKEN: {LINE_CHANNEL_ACCESS_TOKEN}")
    print(f"LINE_CHANNEL_SECRET: {LINE_CHANNEL_SECRET}")
    print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")

# `TEST_VARIABLE` を読み込む
TEST_VARIABLE = os.getenv("TEST_VARIABLE")
print(f"DEBUG: TEST_VARIABLE = {TEST_VARIABLE}")

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

# 全環境変数をダンプする関数
def dump_all_env_vars():
    all_env = {}
    for key, value in os.environ.items():
        # 機密情報をマスクする
        if any(secret_key in key.lower() for secret_key in ['token', 'secret', 'password', 'key', 'auth']):
            val_length = len(value)
            if val_length > 10:
                all_env[key] = f"{value[:5]}...{value[-5:]} (長さ: {val_length})"
            else:
                all_env[key] = f"{'*' * val_length} (長さ: {val_length})"
        else:
            all_env[key] = value
    
    return all_env

# AWS環境の場合、全環境変数をダンプ
if is_aws:
    print("\n===== AWS環境で全環境変数をダンプ =====\n")
    all_env = dump_all_env_vars()
    print(json.dumps(all_env, indent=2, ensure_ascii=False))
