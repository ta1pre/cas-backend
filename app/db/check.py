# app/db/check.py

from sqlalchemy import text
from .session import SessionLocal

def check_db_connection():
    try:
        db = SessionLocal()
        # 「SELECT 1」 を text( ) で囲む
        db.execute(text("SELECT 1"))
        print("✅ データベース接続成功")
    except Exception as e:
        print(f"❌ データベース接続失敗: {e}")
    finally:
        db.close()
