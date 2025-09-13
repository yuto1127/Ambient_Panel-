"""
ハードウェア環境の検出とモック化
M1 MacとRaspberry Pi間でのクロスプラットフォーム開発をサポート
"""

import os
import logging

logger = logging.getLogger(__name__)

def detect_environment() -> bool:
    """
    Raspberry Pi環境かどうかを判定する
    
    Returns:
        bool: Raspberry Pi環境の場合True、それ以外はFalse
    """
    try:
        # Raspberry Piでのみ存在するファイルを確認して判定する
        if os.path.exists('/sys/firmware/devicetree/base/model'):
            with open('/sys/firmware/devicetree/base/model', 'r') as f:
                model_info = f.read().lower()
                if 'raspberry pi' in model_info:
                    logger.info("✅ Running on Raspberry Pi. Real hardware libraries will be loaded.")
                    return True
        
        logger.info("💻 Running on non-Pi machine. Mock libraries will be loaded.")
        return False
        
    except Exception as e:
        logger.warning(f"⚠️ Error detecting environment: {e}")
        logger.info("💻 Defaulting to development mode (non-Pi machine).")
        return False

def get_environment_info() -> dict:
    """
    現在の環境情報を取得する
    
    Returns:
        dict: 環境情報の辞書
    """
    is_pi = detect_environment()
    
    info = {
        "is_raspberry_pi": is_pi,
        "environment": "production" if is_pi else "development",
        "platform": "raspberry_pi" if is_pi else "development_machine"
    }
    
    if is_pi:
        try:
            # Raspberry Piの詳細情報を取得
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'BCM' in cpuinfo:
                    info["cpu_model"] = "Broadcom"
                else:
                    info["cpu_model"] = "Unknown"
        except:
            info["cpu_model"] = "Unknown"
    else:
        info["cpu_model"] = "Development Machine"
    
    return info
