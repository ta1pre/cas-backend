from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# .envファイルが存在する場合のみ読み込み
load_dotenv()

# 環境変数からDATABASE_URLを取得
DATABASE_URL = os.getenv("DATABASE_URL")

# DATABASE_URLが設定されていない場合のエラーハンドリング
if not DATABASE_URL:
    raise ValueError("DATABASE_URL環境変数が設定されていません。")

# ✅ データベースエンジンの作成（JSTに設定）
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "init_command": "SET time_zone = 'Asia/Tokyo'"  # ✅ タイムゾーン設定
    }
)

# ORMの基盤クラス
Base = declarative_base()

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# データベースセッションを取得
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
