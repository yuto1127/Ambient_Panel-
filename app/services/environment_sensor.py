"""
SD40環境センサー（CO2、温度、湿度）の統合
Raspberry Pi環境と開発環境の両方に対応
Adafruit CircuitPythonライブラリを使用
"""

import logging
import time
from typing import Dict, Optional
from app.services.hardware_detection import detect_environment

logger = logging.getLogger(__name__)

# 環境判定
IS_RASPBERRY_PI = detect_environment()

if IS_RASPBERRY_PI:
    try:
        # Raspberry Pi環境の場合、Adafruit CircuitPythonライブラリをインポート
        import board
        import busio
        from adafruit_scd4x import SCD4X
        logger.info("✅ Adafruit CircuitPython SCD4X library loaded.")
    except ImportError as e:
        logger.error(f"❌ Error: Adafruit CircuitPython library not found on Raspberry Pi: {e}")
        raise
else:
    # Mac/PC環境の場合、ダミー（モック）のクラスを定義
    logger.info("💻 Mock SCD4X sensor library loaded.")
    
    class MockSCD4X:
        """Macでの開発用に、本物と同じように振る舞うダミークラス"""
        
        def __init__(self, i2c_bus):
            logger.info("[MOCK] SCD4X sensor initialized.")
            self._co2 = 450
            self._temperature = 25.0
            self._relative_humidity = 50.0
            self._start_periodic_measurement_called = False
        
        def start_periodic_measurement(self):
            """定期的な測定を開始"""
            logger.info("[MOCK] Periodic measurement started.")
            self._start_periodic_measurement_called = True
        
        @property
        def co2(self) -> int:
            """CO2濃度を取得（ppm）"""
            # 開発環境ではランダムな値を返す
            import random
            return random.randint(400, 1000)
        
        @property
        def temperature(self) -> float:
            """温度を取得（℃）"""
            import random
            return round(random.uniform(20.0, 30.0), 1)
        
        @property
        def relative_humidity(self) -> float:
            """相対湿度を取得（%）"""
            import random
            return round(random.uniform(30.0, 70.0), 1)
        
        @property
        def data_ready(self) -> bool:
            """データが準備できているか"""
            return True
    
    # 本物のクラスと同じ名前で、ダミークラスを割り当てる
    SCD4X = MockSCD4X
    
    # モック用のboardとbusio
    class MockBoard:
        SCL = "mock_scl"
        SDA = "mock_sda"
    
    class MockBusio:
        def I2C(self, *args, **kwargs):
            return "mock_i2c_bus"
    
    board = MockBoard()
    busio = MockBusio()

class EnvironmentSensor:
    """SCD4X環境センサー管理クラス"""
    
    def __init__(self):
        self.sensor: Optional[SCD4X] = None
        self.is_initialized = False
        self.last_data = None
        self.last_update_time = None
        self.cache_duration = 10  # 10秒間キャッシュ
        self._initialize_sensor()
    
    def _initialize_sensor(self):
        """センサーの初期化"""
        try:
            if IS_RASPBERRY_PI:
                # Raspberry Pi環境での初期化
                i2c = busio.I2C(board.SCL, board.SDA)
                self.sensor = SCD4X(i2c)
                logger.info("✅ SCD4X sensor initialized on Raspberry Pi")
            else:
                # 開発環境での初期化
                self.sensor = SCD4X("mock_i2c")
                logger.info("💻 Mock SCD4X sensor initialized")
            
            # 定期的な測定を開始
            self.sensor.start_periodic_measurement()
            self.is_initialized = True
            logger.info("✅ Environment sensor initialization completed")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize environment sensor: {e}")
            self.is_initialized = False
    
    def get_environment_data(self) -> Dict[str, float]:
        """
        SCD4Xセンサーから環境データを取得する（キャッシュ機能付き）
        
        Returns:
            Dict[str, float]: 環境データの辞書（温度、湿度、CO2濃度）
        """
        if not self.is_initialized or not self.sensor:
            return {
                "temperature": 0.0,
                "humidity": 0.0,
                "co2": 0,
                "error": "Sensor not initialized"
            }
        
        # キャッシュされたデータがあるかチェック
        current_time = time.time()
        if (self.last_data and self.last_update_time and 
            current_time - self.last_update_time < self.cache_duration):
            logger.debug("Using cached environment data")
            return self.last_data
        
        try:
            # データが準備できているかチェック
            if not self.sensor.data_ready:
                # キャッシュされたデータがあれば返す
                if self.last_data:
                    logger.debug("Data not ready, using cached data")
                    return self.last_data
                return {
                    "temperature": 0.0,
                    "humidity": 0.0,
                    "co2": 0,
                    "error": "Data not ready"
                }
            
            # データを取得
            data = {
                "temperature": round(self.sensor.temperature, 1),
                "humidity": round(self.sensor.relative_humidity, 1),
                "co2": int(self.sensor.CO2),
                "timestamp": current_time
            }
            
            # キャッシュを更新
            self.last_data = data
            self.last_update_time = current_time
            
            logger.debug(f"SCD4X Environment data: {data}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error reading SCD4X environment data: {e}")
            # エラー時はキャッシュされたデータがあれば返す
            if self.last_data:
                logger.debug("Error occurred, using cached data")
                return self.last_data
            return {
                "temperature": 0.0,
                "humidity": 0.0,
                "co2": 0,
                "error": str(e)
            }
    
    def get_sensor_status(self) -> Dict[str, any]:
        """
        SCD4Xセンサーの状態を取得する
        
        Returns:
            Dict[str, any]: センサー状態の辞書
        """
        return {
            "is_initialized": self.is_initialized,
            "is_raspberry_pi": IS_RASPBERRY_PI,
            "sensor_type": "SCD4X",
            "status": "active" if self.is_initialized else "inactive",
            "cache_duration": self.cache_duration,
            "last_update": self.last_update_time,
            "has_cached_data": self.last_data is not None
        }

# グローバルインスタンス
environment_sensor = EnvironmentSensor()
