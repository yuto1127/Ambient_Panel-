"""
環境センサーAPIエンドポイント
SCD40センサーからCO2、温度、湿度データを取得
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from app.services.environment_sensor import environment_sensor

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_environment_data() -> Dict[str, Any]:
    """
    環境データを取得する
    
    Returns:
        Dict[str, Any]: 環境データ（温度、湿度、CO2濃度）
    """
    try:
        data = environment_sensor.get_environment_data()
        return {
            "success": True,
            "data": data,
            "timestamp": data.get("timestamp")
        }
    except Exception as e:
        logger.error(f"Error getting environment data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get environment data: {str(e)}")

@router.get("/status")
async def get_sensor_status() -> Dict[str, Any]:
    """
    センサーの状態を取得する
    
    Returns:
        Dict[str, Any]: センサー状態情報
    """
    try:
        status = environment_sensor.get_sensor_status()
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        logger.error(f"Error getting sensor status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sensor status: {str(e)}")
