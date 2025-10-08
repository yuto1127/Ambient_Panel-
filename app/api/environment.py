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
        logger.info("🔍 API: Getting environment data...")
        data = environment_sensor.get_environment_data()
        logger.info(f"📊 API: Environment data retrieved: {data}")
        
        response = {
            "success": True,
            "data": data
        }
        
        logger.info(f"✅ API: Returning response: {response}")
        return response
        
    except Exception as e:
        logger.error(f"❌ API: Error getting environment data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get environment data: {str(e)}")

@router.get("/status")
async def get_sensor_status() -> Dict[str, Any]:
    """
    センサーの状態を取得する
    
    Returns:
        Dict[str, Any]: センサー状態情報
    """
    try:
        logger.info("🔍 API: Getting sensor status...")
        status = environment_sensor.get_sensor_status()
        logger.info(f"📊 API: Sensor status retrieved: {status}")
        
        response = {
            "success": True,
            "status": status
        }
        
        logger.info(f"✅ API: Returning status response: {response}")
        return response
        
    except Exception as e:
        logger.error(f"❌ API: Error getting sensor status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sensor status: {str(e)}")
