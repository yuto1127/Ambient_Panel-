# Spotify API セットアップガイド

このガイドでは、Ambient PanelアプリケーションでSpotify APIを使用するための設定手順を説明します。

## 1. Spotify Developer Dashboardでの設定

### 1.1 アプリケーションの作成
1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)にアクセス
2. 「Create App」をクリック
3. アプリケーション情報を入力：
   - App name: `Ambient Panel`
   - App description: `Raspberry Pi搭載 多機能情報パネル`
   - Website: `http://localhost:8000`
   - Redirect URI: `http://localhost:8000/api/spotify/callback`

### 1.2 認証情報の取得
1. 作成したアプリケーションをクリック
2. 「Settings」タブで以下を確認・設定：
   - Client ID
   - Client Secret
   - Redirect URIs: `http://localhost:8000/api/spotify/callback`

## 2. 環境変数の設定

`.env`ファイルに以下の設定を追加または確認：

```env
# Spotify Web API認証情報
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/api/spotify/callback
```

## 3. 認証フロー

### 3.1 認証URLの取得
以下のAPIエンドポイントで認証URLを取得：

```bash
curl http://localhost:8000/api/spotify/auth
```

レスポンス例：
```json
{
  "success": true,
  "auth_url": "https://accounts.spotify.com/authorize?client_id=...",
  "message": "Please visit the auth_url to authorize with Spotify"
}
```

### 3.2 Spotify認証
1. 取得した`auth_url`をブラウザで開く
2. Spotifyアカウントでログイン
3. アプリケーションの権限を承認
4. 認証完了後、自動的にコールバックURLにリダイレクトされる

### 3.3 認証状態の確認
以下のAPIエンドポイントで認証状態を確認：

```bash
curl http://localhost:8000/api/spotify/status
```

認証済みの場合：
```json
{
  "success": true,
  "connected": true,
  "authenticated": true,
  "device_name": "Ambient Panel",
  "is_playing": false,
  "message": "Spotify connected and ready"
}
```

## 4. 利用可能なAPIエンドポイント

### 4.1 プレイリスト取得
```bash
curl http://localhost:8000/api/spotify/playlists
```

### 4.2 現在の再生状態
```bash
curl http://localhost:8000/api/spotify/current
```

### 4.3 再生制御
```bash
# 再生
curl -X POST "http://localhost:8000/api/spotify/play?playlist_id=playlist_id_here"

# 一時停止
curl -X POST http://localhost:8000/api/spotify/pause

# 次の曲
curl -X POST http://localhost:8000/api/spotify/next

# 前の曲
curl -X POST http://localhost:8000/api/spotify/previous
```

### 4.4 音量・設定制御
```bash
# 音量設定（0-100）
curl -X POST "http://localhost:8000/api/spotify/volume?volume=50"

# シャッフル設定
curl -X POST "http://localhost:8000/api/spotify/shuffle?state=true"

# リピート設定（off, track, context）
curl -X POST "http://localhost:8000/api/spotify/repeat?state=context"
```

## 5. トラブルシューティング

### 5.1 認証エラー
- Client IDとClient Secretが正しく設定されているか確認
- Redirect URIが正確に設定されているか確認
- トークンファイル（`spotify_tokens.json`）を削除して再認証

### 5.2 デバイスが見つからない場合
- Spotifyアプリが起動しているか確認
- 同じネットワーク上でSpotify Connectが利用可能か確認
- Spotify Premiumアカウントを使用しているか確認

### 5.3 権限エラー
- アプリケーションに必要なスコープが設定されているか確認：
  - `user-read-playback-state`
  - `user-modify-playback-state`
  - `user-read-currently-playing`
  - `playlist-read-private`
  - `user-library-read`

## 6. セキュリティ注意事項

- Client Secretは絶対に公開しない
- `.env`ファイルをバージョン管理に含めない
- 本番環境では適切なHTTPS設定を行う
- 定期的にトークンをリフレッシュする（自動実行）

## 7. 開発時の注意点

- 開発環境では`localhost:8000`を使用
- 本番環境では適切なドメインに変更
- Spotify APIのレート制限に注意
- トークンの有効期限（1時間）を考慮した実装
