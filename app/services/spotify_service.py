"""
Spotify Web API サービス
Spotify APIとの通信を管理するサービスクラス
"""

import os
import base64
import json
from typing import Dict, List, Optional, Any
import aiohttp
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)

class SpotifyService:
    """Spotify Web API サービス"""
    
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8000/api/spotify/callback')
        self.scope = 'user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private user-library-read'
        
        # アクセストークンとリフレッシュトークンの保存先
        self.token_file = 'spotify_tokens.json'
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = 0
        
        # トークンの読み込み
        self._load_tokens()
    
    def _load_tokens(self):
        """保存されたトークンを読み込む"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    tokens = json.load(f)
                    self.access_token = tokens.get('access_token')
                    self.refresh_token = tokens.get('refresh_token')
                    self.token_expires_at = tokens.get('expires_at', 0)
        except Exception as e:
            logger.error(f"トークンの読み込みに失敗: {e}")
    
    def _save_tokens(self):
        """トークンを保存する"""
        try:
            tokens = {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'expires_at': self.token_expires_at
            }
            with open(self.token_file, 'w') as f:
                json.dump(tokens, f)
            logger.info(f"トークンを保存しました。リフレッシュトークン: {'あり' if self.refresh_token else 'なし'}")
        except Exception as e:
            logger.error(f"トークンの保存に失敗: {e}")
    
    def is_authenticated(self) -> bool:
        """認証済みかどうかを確認"""
        if not self.access_token:
            logger.warning("アクセストークンがありません")
            return False
        
        # トークンの有効期限をチェック
        import time
        current_time = time.time()
        time_until_expiry = self.token_expires_at - current_time
        
        logger.info(f"トークン有効期限まで: {time_until_expiry:.0f}秒")
        
        if current_time >= self.token_expires_at - 300:  # 5分前にリフレッシュ
            logger.info("トークンがまもなく期限切れのため、リフレッシュを試行します")
            if self.refresh_token:
                return self._refresh_access_token()
            else:
                logger.error("リフレッシュトークンがありません。再認証が必要です")
                return False
        
        return True
    
    def get_auth_url(self) -> str:
        """認証URLを生成"""
        auth_params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'show_dialog': 'true',
            'access_type': 'offline'  # リフレッシュトークンを取得するために必要
        }
        
        auth_url = f"https://accounts.spotify.com/authorize?{urlencode(auth_params)}"
        return auth_url
    
    async def get_token(self, code: str) -> Dict[str, Any]:
        """認証コードからアクセストークンを取得"""
        if not self.client_id or not self.client_secret:
            return {"success": False, "error": "Spotify credentials not configured"}
        
        # 認証ヘッダーを作成
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://accounts.spotify.com/api/token',
                    data=token_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        token_response = await response.json()
                        
                        self.access_token = token_response['access_token']
                        self.refresh_token = token_response.get('refresh_token')
                        
                        import time
                        self.token_expires_at = time.time() + token_response['expires_in']
                        
                        # リフレッシュトークンが取得できなかった場合の警告
                        if not self.refresh_token:
                            logger.warning("リフレッシュトークンが取得できませんでした。認証URLにaccess_type=offlineが含まれているか確認してください。")
                        
                        self._save_tokens()
                        
                        return {
                            "success": True,
                            "access_token": self.access_token,
                            "expires_in": token_response['expires_in'],
                            "refresh_token": self.refresh_token
                        }
                    else:
                        error_data = await response.json()
                        return {
                            "success": False,
                            "error": error_data.get('error_description', 'Token request failed')
                        }
        except Exception as e:
            logger.error(f"トークン取得エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def _refresh_access_token(self) -> bool:
        """アクセストークンをリフレッシュ"""
        if not self.refresh_token:
            return False
        
        # 同期的なリフレッシュ（非同期でない場合）
        import requests
        
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        token_data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(
                'https://accounts.spotify.com/api/token',
                data=token_data,
                headers=headers
            )
            
            if response.status_code == 200:
                token_response = response.json()
                
                self.access_token = token_response['access_token']
                if 'refresh_token' in token_response:
                    self.refresh_token = token_response['refresh_token']
                
                import time
                self.token_expires_at = time.time() + token_response['expires_in']
                
                self._save_tokens()
                return True
            else:
                logger.error(f"トークンリフレッシュ失敗: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"トークンリフレッシュエラー: {e}")
            return False
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Spotify APIへのリクエストを実行"""
        logger.info(f"Spotify APIリクエスト: {method} {url}")
        
        if not self.is_authenticated():
            logger.error("認証されていません")
            return {"success": False, "error": "Not authenticated"}
        
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.access_token}'
        kwargs['headers'] = headers
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, **kwargs) as response:
                    logger.info(f"Spotify APIレスポンス: {response.status}")
                    
                    # レスポンスのContent-Typeを確認
                    content_type = response.headers.get('content-type', '')
                    logger.info(f"Content-Type: {content_type}")
                    
                    if response.status == 200 or response.status == 204:
                        # 空のレスポンスの場合（204 No Contentは正常）
                        if response.content_length == 0 or response.status == 204:
                            logger.info("空のレスポンスを受信（正常）")
                            return {"success": True, "data": {}}
                        
                        # JSONレスポンスの場合
                        if 'application/json' in content_type:
                            try:
                                data = await response.json()
                                return {"success": True, "data": data}
                            except Exception as json_error:
                                logger.error(f"JSON解析エラー: {json_error}")
                                return {"success": False, "error": "Invalid JSON response"}
                        else:
                            # 非JSONレスポンスの場合でも、空の場合は成功として扱う
                            try:
                                text_data = await response.text()
                                if not text_data.strip():  # 空のテキストの場合
                                    logger.info("空のテキストレスポンスを受信（正常）")
                                    return {"success": True, "data": {}}
                                else:
                                    # Spotify APIのnext/previousエンドポイントは空のレスポンスを返すことがある
                                    if '/me/player/next' in url or '/me/player/previous' in url or '/me/player/play' in url or '/me/player/pause' in url:
                                        logger.info(f"Spotify制御コマンドのレスポンス（正常）: {text_data[:100]}...")
                                        return {"success": True, "data": {}}
                                    else:
                                        logger.warning(f"非JSONレスポンス: {text_data[:200]}...")
                                        return {"success": False, "error": f"Unexpected response type: {content_type}"}
                            except Exception as text_error:
                                logger.error(f"テキスト読み取りエラー: {text_error}")
                                return {"success": False, "error": "Failed to read response"}
                    
                    elif response.status == 401:
                        logger.warning("認証エラー、トークンリフレッシュを試行")
                        # 認証エラーの場合、リフレッシュを試行
                        if self._refresh_access_token():
                            # リトライ
                            headers['Authorization'] = f'Bearer {self.access_token}'
                            async with session.request(method, url, **kwargs) as retry_response:
                                logger.info(f"リトライレスポンス: {retry_response.status}")
                                if retry_response.status == 200 or retry_response.status == 204:
                                    if retry_response.content_length == 0 or retry_response.status == 204:
                                        return {"success": True, "data": {}}
                                    
                                    retry_content_type = retry_response.headers.get('content-type', '')
                                    if 'application/json' in retry_content_type:
                                        try:
                                            retry_data = await retry_response.json()
                                            return {"success": True, "data": retry_data}
                                        except Exception as json_error:
                                            logger.error(f"リトライJSON解析エラー: {json_error}")
                                            return {"success": False, "error": "Invalid JSON response on retry"}
                                    else:
                                        # 非JSONレスポンスの場合でも、空の場合は成功として扱う
                                        try:
                                            retry_text = await retry_response.text()
                                            if not retry_text.strip():
                                                return {"success": True, "data": {}}
                                            else:
                                                # Spotify APIのnext/previousエンドポイントは空のレスポンスを返すことがある
                                                if '/me/player/next' in url or '/me/player/previous' in url or '/me/player/play' in url or '/me/player/pause' in url:
                                                    logger.info(f"Spotify制御コマンドのリトライレスポンス（正常）: {retry_text[:100]}...")
                                                    return {"success": True, "data": {}}
                                                else:
                                                    return {"success": False, "error": f"Unexpected response type on retry: {retry_content_type}"}
                                        except Exception as text_error:
                                            logger.error(f"リトライテキスト読み取りエラー: {text_error}")
                                            return {"success": False, "error": "Failed to read retry response"}
                    
                    # エラーレスポンスの処理
                    try:
                        if 'application/json' in content_type:
                            data = await response.json()
                            error_msg = data.get('error', {}).get('message', f'HTTP {response.status}')
                        else:
                            text_data = await response.text()
                            error_msg = f'HTTP {response.status}: {text_data[:100]}'
                    except Exception as parse_error:
                        error_msg = f'HTTP {response.status}: Failed to parse response'
                    
                    logger.error(f"Spotify APIエラー: {error_msg}")
                    return {"success": False, "error": error_msg}
                    
        except Exception as e:
            logger.error(f"APIリクエストエラー: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_current_playback(self) -> Dict[str, Any]:
        """現在の再生状態を取得"""
        result = await self._make_request('GET', 'https://api.spotify.com/v1/me/player')
        
        if not result['success']:
            return result
        
        playback_data = result['data']
        
        if not playback_data:
            return {
                "success": True,
                "is_playing": False,
                "device_name": "Ambient Panel",
                "message": "No active device"
            }
        
        # デバッグ情報を追加
        logger.info(f"Current playback context: {playback_data.get('context', {})}")
        logger.info(f"Current track: {playback_data.get('item', {}).get('name', 'Unknown')}")
        
        return {
            "success": True,
            "is_playing": playback_data.get('is_playing', False),
            "device_name": playback_data.get('device', {}).get('name', 'Unknown Device'),
            "track": playback_data.get('item', {}),
            "progress_ms": playback_data.get('progress_ms', 0),
            "volume": playback_data.get('device', {}).get('volume_percent', 0),
            "context": playback_data.get('context', {}),
            "shuffle_state": playback_data.get('shuffle_state', False),
            "repeat_state": playback_data.get('repeat_state', 'off')
        }
    
    async def get_playlists(self) -> Dict[str, Any]:
        """プレイリスト一覧を取得"""
        result = await self._make_request('GET', 'https://api.spotify.com/v1/me/playlists?limit=50')
        
        if not result['success']:
            return result
        
        playlists_data = result['data']
        
        playlists = []
        for playlist in playlists_data.get('items', []):
            playlists.append({
                'id': playlist['id'],
                'name': playlist['name'],
                'description': playlist.get('description', ''),
                'tracks_total': playlist['tracks']['total'],
                'images': playlist.get('images', [])
            })
        
        return {
            "success": True,
            "playlists": playlists
        }
    
    async def get_playlist_tracks(self, playlist_id: str) -> Dict[str, Any]:
        """プレイリストの詳細（曲の一覧）を取得（全曲を取得するためページネーション対応）"""
        # 最初のリクエスト（limit=100はSpotify APIの最大値）
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=100'
        all_tracks = []
        total = 0
        
        while url:
            result = await self._make_request('GET', url)
            
            if not result['success']:
                return result
            
            tracks_data = result['data']
            total = tracks_data.get('total', 0)  # 最初のレスポンスからtotalを取得
            
            # トラックを処理
            for item in tracks_data.get('items', []):
                track = item.get('track')
                if track and track['type'] == 'track':  # 削除された曲やポッドキャストは除外
                    all_tracks.append({
                        'id': track['id'],
                        'name': track['name'],
                        'artists': [artist['name'] for artist in track['artists']],
                        'album': track['album']['name'],
                        'duration_ms': track['duration_ms'],
                        'uri': track['uri'],
                        'external_urls': track['external_urls'],
                        'preview_url': track.get('preview_url'),
                        'images': track['album'].get('images', [])
                    })
            
            # 次のページがあるかチェック
            url = tracks_data.get('next')
            if url:
                logger.info(f"次のページを取得中... 現在の取得数: {len(all_tracks)}/{total}")
        
        logger.info(f"プレイリストの全曲を取得しました: {len(all_tracks)}曲")
        
        return {
            "success": True,
            "tracks": all_tracks,
            "total": total
        }
    
    async def get_devices(self) -> Dict[str, Any]:
        """利用可能なデバイス一覧を取得"""
        return await self._make_request('GET', 'https://api.spotify.com/v1/me/player/devices')
    
    async def play(self, context_uri: str = None, uris: List[str] = None, device_id: str = None) -> Dict[str, Any]:
        """再生を開始"""
        # デバイスIDが指定されていない場合、利用可能なデバイスを取得
        if not device_id:
            devices_result = await self.get_devices()
            if devices_result['success'] and devices_result['data'].get('devices'):
                # 最初のアクティブなデバイスを使用
                active_devices = [d for d in devices_result['data']['devices'] if d.get('is_active', False)]
                if active_devices:
                    device_id = active_devices[0]['id']
                else:
                    # アクティブなデバイスがない場合、最初のデバイスを使用
                    device_id = devices_result['data']['devices'][0]['id']
        
        data = {}
        if context_uri:
            data['context_uri'] = context_uri
        elif uris:
            data['uris'] = uris
        
        # デバイスIDが指定されている場合、クエリパラメータに追加
        url = 'https://api.spotify.com/v1/me/player/play'
        if device_id:
            url += f'?device_id={device_id}'
        
        return await self._make_request('PUT', url, json=data)
    
    async def pause(self) -> Dict[str, Any]:
        """再生を一時停止"""
        return await self._make_request('PUT', 'https://api.spotify.com/v1/me/player/pause')
    
    async def next_track(self) -> Dict[str, Any]:
        """次のトラックにスキップ"""
        # アクティブなデバイスを取得
        devices_result = await self.get_devices()
        device_id = None
        
        if devices_result['success'] and devices_result['data'].get('devices'):
            active_devices = [d for d in devices_result['data']['devices'] if d.get('is_active', False)]
            if active_devices:
                device_id = active_devices[0]['id']
                logger.info(f"Using active device: {device_id}")
            else:
                logger.warning("No active device found for next track")
        
        url = 'https://api.spotify.com/v1/me/player/next'
        if device_id:
            url += f'?device_id={device_id}'
        
        result = await self._make_request('POST', url)
        logger.info(f"Next track result: {result}")
        return result
    
    async def previous_track(self) -> Dict[str, Any]:
        """前のトラックに戻る"""
        # アクティブなデバイスを取得
        devices_result = await self.get_devices()
        device_id = None
        
        if devices_result['success'] and devices_result['data'].get('devices'):
            active_devices = [d for d in devices_result['data']['devices'] if d.get('is_active', False)]
            if active_devices:
                device_id = active_devices[0]['id']
                logger.info(f"Using active device: {device_id}")
            else:
                logger.warning("No active device found for previous track")
        
        url = 'https://api.spotify.com/v1/me/player/previous'
        if device_id:
            url += f'?device_id={device_id}'
        
        result = await self._make_request('POST', url)
        logger.info(f"Previous track result: {result}")
        return result
    
    async def set_volume(self, volume_percent: int) -> Dict[str, Any]:
        """音量を設定"""
        if volume_percent < 0 or volume_percent > 100:
            return {"success": False, "error": "Volume must be between 0 and 100"}
        
        return await self._make_request('PUT', f'https://api.spotify.com/v1/me/player/volume?volume_percent={volume_percent}')
    
    async def set_shuffle(self, state: bool) -> Dict[str, Any]:
        """シャッフル状態を設定"""
        return await self._make_request('PUT', f'https://api.spotify.com/v1/me/player/shuffle?state={str(state).lower()}')
    
    async def set_repeat(self, state: str) -> Dict[str, Any]:
        """リピート状態を設定（off, track, context）"""
        if state not in ['off', 'track', 'context']:
            return {"success": False, "error": "Repeat state must be 'off', 'track', or 'context'"}
        
        return await self._make_request('PUT', f'https://api.spotify.com/v1/me/player/repeat?state={state}')

# グローバルインスタンス
spotify_service = SpotifyService()
