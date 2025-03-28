# Dockerfile

# ビルドステージ: 依存関係をインストールする
FROM --platform=linux/amd64 python:3.11-slim AS builder

# セキュリティアップデートとビルドツールのインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Poetryをインストール
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /root/.local/bin/poetry && \
    poetry config virtualenvs.create false && \
    poetry config installer.max-workers 4

# 作業ディレクトリを設定
WORKDIR /build

# 依存関係のファイルだけを先にコピー
COPY pyproject.toml poetry.lock* ./

# 依存関係をインストール（開発用依存関係は除外）
RUN poetry config installer.parallel false && \
    poetry install --without dev --no-interaction --no-ansi --no-root

# 実行ステージ: 実際のアプリケーション実行環境
FROM --platform=linux/amd64 python:3.11-slim

# 必要なパッケージをインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 非root userを作成
RUN useradd -m appuser

# 作業ディレクトリを設定してユーザーに権限を付与
WORKDIR /app
RUN chown appuser:appuser /app

# ビルドステージからの依存関係をコピー
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# アプリのソースコードをコピー
COPY --chown=appuser:appuser ./app /app/app

# 環境変数の設定
ENV PYTHONPATH=/app

# 非rootユーザーに切り替え
USER appuser

# ヘルスチェック設定
HEALTHCHECK CMD curl -f http://localhost:8000/api/v1/health || exit 1

# FastAPIアプリを起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
