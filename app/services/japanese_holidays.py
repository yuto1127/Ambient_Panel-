"""
日本の祝日サービス
日本の祝日を取得し、カレンダーイベントとして提供する
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class JapaneseHolidaysService:
    def __init__(self):
        self.cache_dir = "/tmp/holidays_cache"
        self.cache_duration = 86400  # 24時間キャッシュ
        self._ensure_cache_dir()
        
        # HTTPセッション設定
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AmbientPanel/1.0',
            'Accept': 'application/json'
        })
    
    def _ensure_cache_dir(self):
        """キャッシュディレクトリを作成"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_key(self, year: int) -> str:
        """キャッシュキーを生成"""
        return f"holidays_{year}.json"
    
    def _is_cache_valid(self, cache_file: str) -> bool:
        """キャッシュが有効かチェック"""
        if not os.path.exists(cache_file):
            return False
        
        cache_time = os.path.getmtime(cache_file)
        return (datetime.now().timestamp() - cache_time) < self.cache_duration
    
    def _load_from_cache(self, cache_file: str) -> Optional[List[Dict]]:
        """キャッシュからデータを読み込み"""
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"キャッシュの読み込みに失敗: {e}")
            return None
    
    def _save_to_cache(self, cache_file: str, data: List[Dict]):
        """データをキャッシュに保存"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"キャッシュの保存に失敗: {e}")
    
    def get_holidays_for_year(self, year: int) -> List[Dict[str, Any]]:
        """指定年の祝日を取得"""
        cache_file = os.path.join(self.cache_dir, self._get_cache_key(year))
        
        # キャッシュをチェック
        if self._is_cache_valid(cache_file):
            cached_data = self._load_from_cache(cache_file)
            if cached_data:
                logger.info(f"キャッシュから{year}年の祝日を読み込み")
                return cached_data
        
        try:
            # 祝日APIからデータを取得
            holidays = self._fetch_holidays_from_api(year)
            
            # キャッシュに保存
            self._save_to_cache(cache_file, holidays)
            
            logger.info(f"{year}年の祝日を取得: {len(holidays)}件")
            return holidays
            
        except Exception as e:
            logger.error(f"祝日の取得に失敗: {e}")
            # フォールバック: 基本的な祝日を返す
            return self._get_basic_holidays(year)
    
    def _fetch_holidays_from_api(self, year: int) -> List[Dict[str, Any]]:
        """祝日APIからデータを取得"""
        try:
            # 祝日API（holidays-jp）を使用
            url = f"https://holidays-jp.github.io/api/v1/{year}/date.json"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            holidays_data = response.json()
            
            # イベント形式に変換
            events = []
            for date_str, holiday_name in holidays_data.items():
                try:
                    event_date = datetime.strptime(date_str, "%Y-%m-%d")
                    events.append({
                        'title': holiday_name,
                        'start': event_date.strftime('%Y-%m-%d'),
                        'end': event_date.strftime('%Y-%m-%d'),
                        'all_day': True,
                        'color': '#ff6b6b',  # 祝日用の赤色
                        'location': '',
                        'description': f'日本の祝日: {holiday_name}',
                        'source': 'japanese_holidays'
                    })
                except ValueError as e:
                    logger.warning(f"日付の解析に失敗: {date_str}, {e}")
                    continue
            
            return events
            
        except Exception as e:
            logger.error(f"祝日APIからの取得に失敗: {e}")
            raise
    
    def _get_basic_holidays(self, year: int) -> List[Dict[str, Any]]:
        """基本的な祝日を返す（フォールバック）"""
        basic_holidays = [
            {'month': 1, 'day': 1, 'name': '元日'},
            {'month': 1, 'day': 8, 'name': '成人の日'},  # 2024年以降は第2月曜日
            {'month': 2, 'day': 11, 'name': '建国記念の日'},
            {'month': 2, 'day': 12, 'name': '建国記念の日 振替休日'},  # 土曜日の場合は翌日
            {'month': 2, 'day': 23, 'name': '天皇誕生日'},
            {'month': 3, 'day': 20, 'name': '春分の日'},  # 年によって変動
            {'month': 4, 'day': 29, 'name': '昭和の日'},
            {'month': 5, 'day': 3, 'name': '憲法記念日'},
            {'month': 5, 'day': 4, 'name': 'みどりの日'},
            {'month': 5, 'day': 5, 'name': 'こどもの日'},
            {'month': 7, 'day': 15, 'name': '海の日'},  # 2024年以降は第3月曜日
            {'month': 8, 'day': 11, 'name': '山の日'},
            {'month': 9, 'day': 16, 'name': '敬老の日'},  # 2024年以降は第3月曜日
            {'month': 9, 'day': 22, 'name': '秋分の日'},  # 年によって変動
            {'month': 10, 'day': 14, 'name': 'スポーツの日'},  # 2024年以降は第2月曜日
            {'month': 11, 'day': 3, 'name': '文化の日'},
            {'month': 11, 'day': 23, 'name': '勤労感謝の日'},
        ]
        
        events = []
        for holiday in basic_holidays:
            try:
                # 簡単な日付計算（実際の祝日計算は複雑なので、基本的なもののみ）
                if holiday['month'] == 1 and holiday['day'] == 8:
                    # 成人の日: 1月の第2月曜日
                    first_monday = self._get_first_monday_of_month(year, 1)
                    holiday_date = first_monday + timedelta(days=7)  # 第2月曜日
                elif holiday['month'] == 7 and holiday['day'] == 15:
                    # 海の日: 7月の第3月曜日
                    first_monday = self._get_first_monday_of_month(year, 7)
                    holiday_date = first_monday + timedelta(days=14)  # 第3月曜日
                elif holiday['month'] == 9 and holiday['day'] == 16:
                    # 敬老の日: 9月の第3月曜日
                    first_monday = self._get_first_monday_of_month(year, 9)
                    holiday_date = first_monday + timedelta(days=14)  # 第3月曜日
                elif holiday['month'] == 10 and holiday['day'] == 14:
                    # スポーツの日: 10月の第2月曜日
                    first_monday = self._get_first_monday_of_month(year, 10)
                    holiday_date = first_monday + timedelta(days=7)  # 第2月曜日
                else:
                    # 固定日付の祝日
                    holiday_date = datetime(year, holiday['month'], holiday['day'])
                
                events.append({
                    'title': holiday['name'],
                    'start': holiday_date.strftime('%Y-%m-%d'),
                    'end': holiday_date.strftime('%Y-%m-%d'),
                    'all_day': True,
                    'color': '#ff6b6b',  # 祝日用の赤色
                    'location': '',
                    'description': f'日本の祝日: {holiday["name"]}',
                    'source': 'japanese_holidays'
                })
                
            except Exception as e:
                logger.warning(f"祝日の計算に失敗: {holiday['name']}, {e}")
                continue
        
        return events
    
    def _get_first_monday_of_month(self, year: int, month: int) -> datetime:
        """指定月の第1月曜日を取得"""
        first_day = datetime(year, month, 1)
        days_until_monday = (7 - first_day.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        return first_day + timedelta(days=days_until_monday)
    
    def get_holidays_for_month(self, year: int, month: int) -> List[Dict[str, Any]]:
        """指定月の祝日を取得"""
        all_holidays = self.get_holidays_for_year(year)
        
        # 指定月の祝日をフィルタリング
        month_holidays = []
        for holiday in all_holidays:
            try:
                holiday_date = datetime.strptime(holiday['start'], '%Y-%m-%d')
                if holiday_date.month == month:
                    month_holidays.append(holiday)
            except ValueError:
                continue
        
        return month_holidays
    
    def get_holidays_for_day(self, year: int, month: int, day: int) -> List[Dict[str, Any]]:
        """指定日の祝日を取得"""
        all_holidays = self.get_holidays_for_year(year)
        
        # 指定日の祝日をフィルタリング
        day_holidays = []
        target_date = datetime(year, month, day)
        
        for holiday in all_holidays:
            try:
                holiday_date = datetime.strptime(holiday['start'], '%Y-%m-%d')
                if holiday_date.date() == target_date.date():
                    day_holidays.append(holiday)
            except ValueError:
                continue
        
        return day_holidays
