FROM node:18-alpine AS builder

WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# Python と pip をインストール
RUN apk add --no-cache python3 py3-pip

# 依存関係をインストール
COPY package*.json ./
RUN npm install

# requirements-pi.txt をインストール
COPY requirements-pi.txt ./
RUN pip install --no-cache-dir --no-binary :all: -r requirements-pi.txt

# 依存関係をインストール
RUN npm install

# ソースコードをコピー
COPY . .

# アプリケーションをビルド
RUN npm run build

# 本番用イメージ
FROM nginx:alpine

# ビルドされたファイルをコピー
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx設定をコピー
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
