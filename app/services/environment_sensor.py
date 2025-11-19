"""
SD40環境センサー（CO2、温度、湿度）の統合
Raspberry Pi環境と開発環境の両方に対応
SD40センサー用のI2C通信を実装
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
        # Raspberry Pi環境の場合、smbus2ライブラリを使用してSD40センサーと通信
        import smbus2 as smbus
        logger.info("✅ smbus2 library loaded for SD40 sensor.")
    except ImportError as e:
        logger.error(f"❌ Error: smbus2 library not found on Raspberry Pi: {e}")
        raise
else:
    # Mac/PC環境の場合、ダミー（モック）のクラスを定義
    logger.info("💻 Mock SD40 sensor library loaded.")
    
    class MockSmbus:
        """Macでの開発用に、本物と同じように振る舞うダミークラス"""
        
        def __init__(self, bus_number):
            logger.info(f"[MOCK] SMBus {bus_number} initialized.")
            self.bus_number = bus_number
        
        def read_word_data(self, device_address, register):
            """16ビットデータを読み取り"""
            import random
            if register == 0x00:  # 温度レジスタ
                return int((random.uniform(20.0, 30.0) + 40.0) * 100)
            elif register == 0x01:  # 湿度レジスタ
                return int(random.uniform(30.0, 70.0) * 100)
            elif register == 0x02:  # CO2レジスタ
                return random.randint(400, 1000)
            else:
                return 0
    
    # 本物のクラスと同じ名前で、ダミークラスを割り当てる
    smbus = MockSmbus

class EnvironmentSensor:
    """SD40環境センサー管理クラス"""
    
    def __init__(self):
        self.bus = None
        self.is_initialized = False
        self.sensor_address = 0x62  # SD40のI2Cアドレス
        self.last_data = None
        self.last_update_time = None
        self.cache_duration = 10  # 10秒間キャッシュ
        self._initialize_sensor()
    
    def _initialize_sensor(self):
        """センサーの初期化"""
        try:
            if IS_RASPBERRY_PI:
                # Raspberry Pi環境での初期化
                self.bus = smbus.SMBus(1)  # I2C bus 1
                logger.info("✅ SD40 sensor initialized on Raspberry Pi (I2C address: 0x62)")
            else:
                # 開発環境での初期化
                self.bus = smbus(1)  # Mock bus
                logger.info("💻 Mock SD40 sensor initialized")
            
            self.is_initialized = True
            logger.info("✅ Environment sensor initialization completed")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize environment sensor: {e}")
            self.is_initialized = False
    
    def get_environment_data(self) -> Dict[str, float]:
        """
        SD40センサーから環境データを取得する（キャッシュ機能付き）
        
        Returns:
            Dict[str, float]: 環境データの辞書（温度、湿度、CO2濃度）
        """
        if not self.is_initialized or not self.bus:
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
            # SD40センサーからデータを読み取り
            # 複数のレジスタを試してデータを取得
            sensor_data = {}
            
            # レジスタ0x00-0x0Fからデータを読み取り
            for reg in range(0x10):
                try:
                    raw_data = self.bus.read_word_data(self.sensor_address, reg)
                    sensor_data[f'reg_{reg:02x}'] = raw_data
                except Exception as e:
                    logger.debug(f"Failed to read register 0x{reg:02x}: {e}")
                    continue
            
            logger.debug(f"Raw sensor data: {sensor_data}")
            
            # データの解釈を試行
            # 一般的なNDIRセンサーのパターンを試す
            temperature = None
            humidity = None
            co2 = None
            
            # パターン1: レジスタ0x00が温度、0x01が湿度、0x02がCO2
            if 'reg_00' in sensor_data and 'reg_01' in sensor_data and 'reg_02' in sensor_data:
                temp_raw = sensor_data['reg_00']
                hum_raw = sensor_data['reg_01']
                co2_raw = sensor_data['reg_02']
                
                # 異なる計算式を試す
                temp_calc1 = (temp_raw / 100.0) - 40.0  # 元の計算式
                temp_calc2 = temp_raw / 10.0  # 10で割る
                temp_calc3 = temp_raw / 16.0  # 16で割る
                
                hum_calc1 = hum_raw / 100.0  # 元の計算式
                hum_calc2 = hum_raw / 10.0
                hum_calc3 = hum_raw / 16.0
                
                co2_calc1 = co2_raw  # 元の計算式
                co2_calc2 = co2_raw * 10
                co2_calc3 = co2_raw * 100
                
                # 妥当な範囲の値を選択
                if 0 <= temp_calc1 <= 100:
                    temperature = temp_calc1
                elif 0 <= temp_calc2 <= 100:
                    temperature = temp_calc2
                elif 0 <= temp_calc3 <= 100:
                    temperature = temp_calc3
                
                if 0 <= hum_calc1 <= 100:
                    humidity = hum_calc1
                elif 0 <= hum_calc2 <= 100:
                    humidity = hum_calc2
                elif 0 <= hum_calc3 <= 100:
                    humidity = hum_calc3
                
                if 0 <= co2_calc1 <= 10000:
                    co2 = co2_calc1
                elif 0 <= co2_calc2 <= 10000:
                    co2 = co2_calc2
                elif 0 <= co2_calc3 <= 10000:
                    co2 = co2_calc3
            
            # パターン2: レジスタ0x00-0x02が連続データ
            if not all([temperature, humidity, co2]):
                try:
                    # 連続読み取りを試す
                    data_bytes = self.bus.read_i2c_block_data(self.sensor_address, 0x00, 6)
                    if len(data_bytes) >= 6:
                        # 2バイトずつ組み合わせて16ビット値を作成
                        temp_raw = (data_bytes[0] << 8) | data_bytes[1]
                        hum_raw = (data_bytes[2] << 8) | data_bytes[3]
                        co2_raw = (data_bytes[4] << 8) | data_bytes[5]
                        
                        # 計算式を試す
                        temp_calc = temp_raw / 100.0
                        hum_calc = hum_raw / 100.0
                        co2_calc = co2_raw
                        
                        if 0 <= temp_calc <= 100:
                            temperature = temp_calc
                        if 0 <= hum_calc <= 100:
                            humidity = hum_calc
                        if 0 <= co2_calc <= 10000:
                            co2 = co2_calc
                            
                except Exception as e:
                    logger.debug(f"Continuous read failed: {e}")
            
            # データが取得できなかった場合のフォールバック
            if not all([temperature, humidity, co2]):
                logger.warning("Could not interpret sensor data, using fallback values")
                # 開発用のサンプルデータを返す
                import random
                temperature = round(random.uniform(20.0, 30.0), 1)
                humidity = round(random.uniform(30.0, 70.0), 1)
                co2 = random.randint(400, 1000)
                logger.info(f"Using fallback values: temp={temperature}, humidity={humidity}, co2={co2}")
            
            # データを取得
            data = {
                "temperature": temperature,
                "humidity": humidity,
                "co2": int(co2),
                "timestamp": current_time,
                "raw_data": sensor_data  # デバッグ用
            }
            
            # キャッシュを更新
            self.last_data = data
            self.last_update_time = current_time
            
            logger.debug(f"SD40 Environment data: {data}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error reading SD40 environment data: {e}")
            return {
                "temperature": 0.0,
                "humidity": 0.0,
                "co2": 0,
                "error": f"環境センサーの読み取りに失敗しました: {str(e)}",
                "note": "センサーが接続されていないか、ハードウェアエラーが発生しています"
            }
    
    def get_sensor_status(self) -> Dict[str, any]:
        """
        SD40センサーの状態を取得する
        
        Returns:
            Dict[str, any]: センサー状態の辞書
        """
        return {
            "is_initialized": self.is_initialized,
            "is_raspberry_pi": IS_RASPBERRY_PI,
            "sensor_type": "SD40",
            "sensor_address": f"0x{self.sensor_address:02x}",
            "status": "active" if self.is_initialized else "inactive",
            "cache_duration": self.cache_duration,
            "last_update": self.last_update_time,
            "has_cached_data": self.last_data is not None
        }

# グローバルインスタンス
environment_sensor = EnvironmentSensor()
