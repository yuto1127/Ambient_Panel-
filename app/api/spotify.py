"""
Spotify APIエンドポイント
プレイリスト、再生制御、現在の再生状態を管理
"""

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from typing import Dict, Any, List, Optional
import logging
import os
from datetime import datetime

from app.services.spotify_service import spotify_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/auth")
async def get_auth_url() -> Dict[str, Any]:
    """
    Spotify認証URLを取得
    
    Returns:
        Dict[str, Any]: 認証URL
    """
    try:
        auth_url = spotify_service.get_auth_url()
        return {
            "success": True,
            "auth_url": auth_url,
            "message": "Please visit the auth_url to authorize with Spotify"
        }
    except Exception as e:
        logger.error(f"Auth URL error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/callback")
async def spotify_callback(code: Optional[str] = Query(None)) -> Dict[str, Any]:
    """
    Spotify認証コールバック
    
    Args:
        code: Spotifyから返される認証コード
    
    Returns:
        Dict[str, Any]: 認証結果
    """
    if not code:
        return {
            "success": False,
            "error": "Authorization code not provided"
        }
    
    try:
        result = await spotify_service.get_token(code)
        return result
    except Exception as e:
        logger.error(f"Callback error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/volume")
async def set_volume(volume: int = Query(..., ge=0, le=100)) -> Dict[str, Any]:
    """
    音量を設定
    
    Args:
        volume: 音量（0-100）
    
    Returns:
        Dict[str, Any]: 設定結果
    """
    try:
        result = await spotify_service.set_volume(volume)
        return result
    except Exception as e:
        logger.error(f"Volume error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/shuffle")
async def set_shuffle(state: bool = Query(...)) -> Dict[str, Any]:
    """
    シャッフル状態を設定
    
    Args:
        state: シャッフル状態（true/false）
    
    Returns:
        Dict[str, Any]: 設定結果
    """
    try:
        result = await spotify_service.set_shuffle(state)
        return result
    except Exception as e:
        logger.error(f"Shuffle error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/repeat")
async def set_repeat(state: str = Query(..., regex="^(off|track|context)$")) -> Dict[str, Any]:
    """
    リピート状態を設定
    
    Args:
        state: リピート状態（off, track, context）
    
    Returns:
        Dict[str, Any]: 設定結果
    """
    try:
        result = await spotify_service.set_repeat(state)
        return result
    except Exception as e:
        logger.error(f"Repeat error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/status")
async def get_spotify_status() -> Dict[str, Any]:
    """
    Spotify接続状態を取得
    
    Returns:
        Dict[str, Any]: Spotify接続状態
    """
    try:
        is_authenticated = spotify_service.is_authenticated()
        
        if is_authenticated:
            playback_info = await spotify_service.get_current_playback()
            return {
                "success": True,
                "connected": True,
                "authenticated": True,
                "device_name": playback_info.get("device_name", "Ambient Panel"),
                "is_playing": playback_info.get("is_playing", False),
                "message": "Spotify connected and ready"
            }
        else:
            return {
                "success": True,
                "connected": False,
                "authenticated": False,
                "device_name": "Ambient Panel",
                "message": "Not authenticated. Please authorize with Spotify."
            }
    except Exception as e:
        logger.error(f"Spotify status error: {e}")
        return {
            "success": False,
            "connected": False,
            "authenticated": False,
            "device_name": "Ambient Panel",
            "error": str(e)
        }

@router.get("/playlists")
async def get_playlists() -> Dict[str, Any]:
    """
    ユーザーのプレイリスト一覧を取得
    
    Returns:
        Dict[str, Any]: プレイリスト一覧
    """
    try:
        result = await spotify_service.get_playlists()
        return result
    except Exception as e:
        logger.error(f"Playlists error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/playlists/{playlist_id}")
async def get_playlist_tracks(playlist_id: str) -> Dict[str, Any]:
    """
    プレイリストの詳細（曲の一覧）を取得
    
    Args:
        playlist_id: プレイリストのID
    
    Returns:
        Dict[str, Any]: プレイリストの曲一覧
    """
    try:
        result = await spotify_service.get_playlist_tracks(playlist_id)
        return result
    except Exception as e:
        logger.error(f"Playlist tracks error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/devices")
async def get_devices() -> Dict[str, Any]:
    """
    利用可能なデバイス一覧を取得
    
    Returns:
        Dict[str, Any]: デバイス一覧
    """
    try:
        result = await spotify_service.get_devices()
        return result
    except Exception as e:
        logger.error(f"Devices error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/current")
async def get_current_playback() -> Dict[str, Any]:
    """
    現在の再生状態を取得
    
    Returns:
        Dict[str, Any]: 現在の再生情報
    """
    try:
        result = await spotify_service.get_current_playback()
        return result
    except Exception as e:
        logger.error(f"Current playback error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/play")
async def play_track(
    playlist_id: Optional[str] = Query(None, description="Playlist ID to play"),
    track_uri: Optional[str] = Query(None, description="Track URI to play")
) -> Dict[str, Any]:
    """
    楽曲の再生
    
    Args:
        playlist_id: 再生するプレイリストのID
        track_uri: 再生する楽曲のURI
    
    Returns:
        Dict[str, Any]: 再生結果
    """
    try:
        if playlist_id:
            context_uri = f"spotify:playlist:{playlist_id}"
            result = await spotify_service.play(context_uri=context_uri)
        elif track_uri:
            result = await spotify_service.play(uris=[track_uri])
        else:
            result = await spotify_service.play()
        
        return result
    except Exception as e:
        logger.error(f"Play error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/pause")
async def pause_playback() -> Dict[str, Any]:
    """
    再生を一時停止
    
    Returns:
        Dict[str, Any]: 一時停止結果
    """
    try:
        result = await spotify_service.pause()
        return result
    except Exception as e:
        logger.error(f"Pause error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/next")
async def next_track() -> Dict[str, Any]:
    """
    次の楽曲にスキップ
    
    Returns:
        Dict[str, Any]: スキップ結果
    """
    try:
        result = await spotify_service.next_track()
        return result
    except Exception as e:
        logger.error(f"Next track error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/previous")
async def previous_track() -> Dict[str, Any]:
    """
    前の楽曲に戻る
    
    Returns:
        Dict[str, Any]: 戻る結果
    """
    try:
        result = await spotify_service.previous_track()
        return result
    except Exception as e:
        logger.error(f"Previous track error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
