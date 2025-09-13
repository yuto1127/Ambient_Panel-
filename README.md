# Ambient Panel - 多機能情報パネル

Raspberry Pi搭載の多機能情報パネルプロジェクトです。タッチ操作で環境データ、Spotify、カレンダー、ニュース、タイマー機能を統合した情報表示システムです。

## 機能

- **環境モニタリング**: SCD40センサーによるCO2、温度、湿度の測定
- **Spotify統合**: プレイリスト表示と再生制御
- **天気情報**: OpenWeatherMap APIによる現在の天気と予報
- **カレンダー**: Google Calendar連携による予定表示
- **ニュース**: NewsAPI.orgによる最新ニュース表示
- **タイマー**: 通常タイマーとポモドーロタイマー
- **タッチUI**: 10.1インチタッチモニター対応
- **モダンUI**: Svelteによる軽量で高速なフロントエンド

## ハードウェア要件

- Raspberry Pi 5
- EVICIV 10.1インチタッチモニター（指定モデル）
- SCD40環境センサー
- HDMI/USBケーブル
- ジャンパーワイヤー（SCD40接続用）

## ソフトウェア要件

- Raspberry Pi OS Bookworm (64-bit)
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ (フロントエンド開発用)

## セットアップ

### 1. 環境変数の設定

```bash
cp env.example .env
# .envファイルを編集してAPIキーなどを設定
```

### 2. 開発環境での実行

```bash
# 開発用Docker Composeで起動（フロントエンド + バックエンド）
docker-compose -f docker-compose.dev.yml up --build
```

フロントエンド: http://localhost:5173  
バックエンドAPI: http://localhost:8000

### 3. 本番環境での実行

```bash
# 本番用Docker Composeで起動
docker-compose -f docker-compose.prod.yml up --build -d
```

アプリケーション: http://localhost:80

## API設定

### Spotify Web API
1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)でアプリを作成
2. Client IDとClient Secretを取得
3. `.env`ファイルに設定

### OpenWeatherMap API
1. [OpenWeatherMap](https://openweathermap.org/api)でAPIキーを取得
2. `.env`ファイルに設定

### Google Calendar API
1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Calendar APIを有効化
3. OAuth 2.0認証情報を作成
4. `credentials.json`をダウンロードしてプロジェクトルートに配置

### NewsAPI.org
1. [NewsAPI.org](https://newsapi.org/)でAPIキーを取得
2. `.env`ファイルに設定

## プロジェクト構造

```
Ambient_Panel-/
├── app/                     # FastAPIバックエンド
│   ├── api/                 # APIエンドポイント
│   ├── models/              # データモデル
│   ├── services/            # ビジネスロジック
│   └── main.py             # メインアプリケーション
├── frontend/               # Svelteフロントエンド
│   ├── src/
│   │   ├── lib/            # ライブラリとコンポーネント
│   │   │   ├── components/ # Svelteコンポーネント
│   │   │   ├── stores/    # Svelteストア
│   │   │   └── utils/     # ユーティリティ関数
│   │   └── routes/        # ページルート
│   ├── package.json        # Node.js依存関係
│   └── Dockerfile         # フロントエンドDocker設定
├── docker-compose.dev.yml   # 開発環境設定
├── docker-compose.prod.yml  # 本番環境設定
├── Dockerfile              # バックエンドDocker設定
├── requirements.txt        # Python依存関係
├── requirements-pi.txt     # Raspberry Pi専用依存関係
└── README.md              # このファイル
```

## 開発

### フロントエンド開発
Svelteを使用したモダンなフロントエンド開発が可能です。

```bash
# フロントエンドのみ開発
cd frontend
npm install
npm run dev
```

### クロスプラットフォーム開発
このプロジェクトはM1 MacとRaspberry Pi間でのクロスプラットフォーム開発をサポートしています。

- **M1 Mac**: モックライブラリを使用して開発
- **Raspberry Pi**: 実際のハードウェアライブラリを使用

### 環境判定
アプリケーションは自動的に実行環境を検出し、適切なライブラリを読み込みます。

### Svelteの特徴
- **軽量**: バンドルサイズが小さく、高速な読み込み
- **リアクティブ**: 状態変更の自動更新
- **コンポーネント指向**: 再利用可能なUIコンポーネント
- **TypeScript対応**: 型安全性の確保

## ライセンス

MIT License

## 貢献

プルリクエストやイシューの報告を歓迎します。

## トラブルシューティング

### よくある問題

1. **SCD40センサーが認識されない**
   - I2Cインターフェースが有効になっているか確認
   - 配線が正しいか確認
   - `sudo i2cdetect -y 1`でセンサーを検出

2. **Spotify接続エラー**
   - API認証情報が正しいか確認
   - ネットワーク接続を確認

3. **Docker起動エラー**
   - Dockerが正しくインストールされているか確認
   - ポート80が使用されていないか確認