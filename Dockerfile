# --- ステージ1: 全環境共通のベースイメージ ---
FROM python:3.11-slim AS base

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    i2c-tools \
    libi2c-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 共通ライブラリをインストール
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# --- ステージ2: 開発環境用イメージ (M1 Macで使う) ---
FROM base AS dev
# 何も追加しない（ラズパイ専用ライブラリは不要）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]

# --- ステージ3: 本番環境用イメージ (Raspberry Piで使う) ---
FROM base AS prod
# ラズパイ専用ライブラリを追加でインストール
COPY requirements-pi.txt .
RUN pip install --no-cache-dir -r requirements-pi.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
