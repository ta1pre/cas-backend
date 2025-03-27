import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
from app.db.session import Base, engine  # SQLAlchemy の `Base` を取得

# 📌 プロジェクトのルートパスを `sys.path` に追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 📌 `.env` をロード
load_dotenv()

# 📌 FastAPI の `config.py` から `DATABASE_URL` を取得
from app.core.config import DATABASE_URL

# 🚨 `DATABASE_URL` が None の場合はエラー
if not DATABASE_URL:
    raise ValueError("🚨 DATABASE_URL が設定されていません！ `.env` を確認してください。")

# 📌 Alembic の設定を取得
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# 📌 ログ設定
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 📌 `app/db/models/` 以下のすべてのモデルをインポート
import importlib

models_dir = os.path.join(os.path.dirname(__file__), "../app/db/models")
for filename in os.listdir(models_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"app.db.models.{filename[:-3]}"
        importlib.import_module(module_name)

# 📌 正しいタイミングで `Base.metadata` をセット
print("=== DEBUG: Base.metadata.tables BEFORE ===")
print(Base.metadata.tables.keys())  # ここでテーブル一覧を出力
print("=== DEBUG END ===")

target_metadata = Base.metadata

# 📌 Alembic に「既存のテーブルを削除させない」設定
def include_object(obj, name, type_, reflected, compare_to):
    if type_ == "table" and reflected and compare_to is None:
        return False  # ✅ 既存のテーブルは削除しない
    return True

def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
