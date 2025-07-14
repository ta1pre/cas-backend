import os
from dotenv import load_dotenv
import logging

# -----------------------------------------------------------------------------------
# 環境変数 `VERBOSE_ENV_LOGS` が "1" のときだけ各種 print を出力する。
# Alembic など CLI ツール実行時の冗長ログを抑制するため、デフォルトは非表示。
# -----------------------------------------------------------------------------------
VERBOSE_ENV_LOGS = os.getenv("VERBOSE_ENV_LOGS", "0") == "1"

if not VERBOSE_ENV_LOGS:
    # `print` をダミー関数に置き換え、標準出力への冗長な出力を抑制
    def _noop(*args, **kwargs):
        pass
    print = _noop  # type: ignore

import json
import sys

# ロガーの設定
logger = logging.getLogger("config")

# `.env` を明示的に指定してロード
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
if os.path.exists(dotenv_path):
    print(f"✅ `.env` をロード: {dotenv_path}")
    load_dotenv(dotenv_path, override=True)  # ← `override=True` を必ず設定
    
    # 特定の重要な環境変数を強制的に再ロード
    with open(dotenv_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if key in ['FRONTEND_URL', 'REDIRECT_URI']:
                    os.environ[key] = value
                    print(f"🔄 強制的に再設定: {key}={value}")
else:
    print("💡 `.env` が見つかりません。環境変数から直接読み込みます。")

# AWS環境かどうかを判定
is_aws = os.getenv("AWS_EXECUTION_ENV") is not None or os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None
if is_aws:
    print("\n===== AWS環境で実行中 =====\n")
    logger.info("AWS環境で実行中")
else:
    print("\n===== ローカル環境で実行中 =====\n")
    logger.info("ローカル環境で実行中")

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
            logger.info(f"環境変数 {name} が設定されています")
        else:
            val_length = len(value)
            if val_length > 10:
                masked_val = value[:5] + "*" * (val_length - 10) + value[-5:]
                print(f"✅ {name}: {masked_val} (長さ: {val_length}文字)")
                logger.info(f"環境変数 {name} が設定されています (長さ: {val_length}文字)")
            else:
                print(f"✅ {name}: {'*' * val_length} (長さ: {val_length}文字)")
                logger.info(f"環境変数 {name} が設定されています (長さ: {val_length}文字)")
    else:
        print(f"❌ {name} が設定されていません")
        logger.error(f"環境変数 {name} が設定されていません")
        if name in ["LINE_CHANNEL_ACCESS_TOKEN", "LINE_CHANNEL_SECRET"]:
            print(f"⚠️ {name} が設定されていないため、LINE Messaging APIが正常に動作しません")
            logger.critical(f"{name} が設定されていないため、LINE Messaging APIが正常に動作しません")

# 必要な環境変数の値を確認
print("\n===== 必要な環境変数の値を確認 =====\n")
check_env_var("LINE_CHANNEL_ACCESS_TOKEN", LINE_CHANNEL_ACCESS_TOKEN)
check_env_var("LINE_CHANNEL_SECRET", LINE_CHANNEL_SECRET)
check_env_var("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
check_env_var("DATABASE_URL", DATABASE_URL, True)
check_env_var("REDIRECT_URI", REDIRECT_URI, True)

# AWS環境の場合、環境変数の値を詳細出力
if is_aws:
    print("\n===== AWS環境で環境変数の値を出力 =====\n")
    logger.info("AWS環境で環境変数の詳細確認を開始")
    
    # LINE Messaging API関連の環境変数を詳細チェック
    if LINE_CHANNEL_ACCESS_TOKEN:
        token_length = len(LINE_CHANNEL_ACCESS_TOKEN)
        print(f"LINE_CHANNEL_ACCESS_TOKEN: {LINE_CHANNEL_ACCESS_TOKEN[:5]}...{LINE_CHANNEL_ACCESS_TOKEN[-5:]} (長さ: {token_length}文字)")
        logger.info(f"LINE_CHANNEL_ACCESS_TOKEN の長さは {token_length} 文字です")
        
        # トークンの形式チェック
        if not LINE_CHANNEL_ACCESS_TOKEN.startswith("Bearer") and not LINE_CHANNEL_ACCESS_TOKEN.startswith("bearer"):
            print("ℹ️ LINE_CHANNEL_ACCESS_TOKEN は 'Bearer' で始まっていません。自動的に追加されます。")
            logger.warning("LINE_CHANNEL_ACCESS_TOKEN は 'Bearer' で始まっていません")
    else:
        print("❌ LINE_CHANNEL_ACCESS_TOKEN が設定されていません！")
        logger.critical("LINE_CHANNEL_ACCESS_TOKEN が設定されていません！")
    
    if LINE_CHANNEL_SECRET:
        secret_length = len(LINE_CHANNEL_SECRET)
        print(f"LINE_CHANNEL_SECRET: {LINE_CHANNEL_SECRET[:3]}...{LINE_CHANNEL_SECRET[-3:]} (長さ: {secret_length}文字)")
        logger.info(f"LINE_CHANNEL_SECRET の長さは {secret_length} 文字です")
    else:
        print("❌ LINE_CHANNEL_SECRET が設定されていません！署名検証ができません！")
        logger.critical("LINE_CHANNEL_SECRET が設定されていません！署名検証ができません！")
    
    # OpenAI APIキーの確認
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        key_length = len(openai_key)
        print(f"OPENAI_API_KEY: {openai_key[:3]}...{openai_key[-3:]} (長さ: {key_length}文字)")
        logger.info(f"OPENAI_API_KEY の長さは {key_length} 文字です")
    else:
        print("❌ OPENAI_API_KEY が設定されていません！")
        logger.critical("OPENAI_API_KEY が設定されていません！")

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

# Stripe Keys
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET") # Webhook署名検証用

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
    logger.info("AWS環境で全環境変数のダンプを完了")
    
    # AWS特有の環境変数の確認
    aws_vars = {
        "AWS_REGION": os.getenv("AWS_REGION"),
        "AWS_LAMBDA_FUNCTION_NAME": os.getenv("AWS_LAMBDA_FUNCTION_NAME"),
        "AWS_LAMBDA_FUNCTION_VERSION": os.getenv("AWS_LAMBDA_FUNCTION_VERSION"),
        "AWS_EXECUTION_ENV": os.getenv("AWS_EXECUTION_ENV")
    }
    print("\n===== AWS特有の環境変数 =====\n")
    print(json.dumps(aws_vars, indent=2, ensure_ascii=False))
    logger.info("AWS特有の環境変数の確認を完了")
