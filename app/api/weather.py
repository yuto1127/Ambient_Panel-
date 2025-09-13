"""
天気APIエンドポイント
OpenWeatherMap APIを使用して天気情報を取得
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import os
import requests
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# 天気APIの設定
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_LATITUDE = os.getenv("WEATHER_LATITUDE", "36.3238")  # 高崎市の緯度
WEATHER_LONGITUDE = os.getenv("WEATHER_LONGITUDE", "139.0043")  # 高崎市の経度

@router.get("/current")
async def get_current_weather() -> Dict[str, Any]:
    """
    現在の天気情報を取得
    
    Returns:
        Dict[str, Any]: 現在の天気情報
    """
    if not WEATHER_API_KEY:
        logger.warning("Weather API key not configured, returning mock data")
        return {
            "success": True,
            "data": {
                "location": "高崎市",
                "temperature": 22.5,
                "humidity": 65,
                "description": "晴れ",
                "icon": "01d",
                "wind_speed": 3.2,
                "pressure": 1013,
                "timestamp": datetime.now().isoformat()
            },
            "source": "mock"
        }
    
    try:
        # OpenWeatherMap APIから現在の天気を取得
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": WEATHER_LATITUDE,
            "lon": WEATHER_LONGITUDE,
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "ja"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        weather_data = {
            "location": data.get("name", "高崎市"),
            "temperature": round(data["main"]["temp"], 1),
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "wind_speed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": weather_data,
            "source": "api"
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather data: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/forecast")
async def get_weather_forecast() -> Dict[str, Any]:
    """
    5日間の天気予報を取得
    
    Returns:
        Dict[str, Any]: 天気予報情報
    """
    if not WEATHER_API_KEY:
        logger.warning("Weather API key not configured, returning mock data")
        return {
            "success": True,
            "data": {
                "forecast": [
                    {
                        "date": "2024-01-01",
                        "temperature_max": 25.0,
                        "temperature_min": 15.0,
                        "description": "晴れ",
                        "icon": "01d"
                    },
                    {
                        "date": "2024-01-02",
                        "temperature_max": 23.0,
                        "temperature_min": 13.0,
                        "description": "曇り",
                        "icon": "02d"
                    }
                ]
            },
            "source": "mock"
        }
    
    try:
        # OpenWeatherMap APIから5日間の予報を取得
        url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": WEATHER_LATITUDE,
            "lon": WEATHER_LONGITUDE,
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "ja"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # 日別の予報データを整理
        forecast_data = []
        for item in data["list"][:5]:  # 最初の5日分
            forecast_data.append({
                "date": item["dt_txt"][:10],
                "temperature_max": round(item["main"]["temp_max"], 1),
                "temperature_min": round(item["main"]["temp_min"], 1),
                "description": item["weather"][0]["description"],
                "icon": item["weather"][0]["icon"]
            })
        
        return {
            "success": True,
            "data": {
                "forecast": forecast_data
            },
            "source": "api"
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather forecast: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather forecast: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
