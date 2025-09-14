"""
iCloudカレンダーサービス
iCloudの公開カレンダーから情報を取得し、統合する
"""

import requests
import logging
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from icalendar import Calendar
import pytz
from dateutil import parser as date_parser
import json
import os

logger = logging.getLogger(__name__)

class ICloudCalendarService:
    def __init__(self):
        self.calendar_urls = [
            "https://p52-caldav.icloud.com/published/2/MjAxMTg4NDQzMzQyMDExON96CchJBr3tDJgJsTIf_PrHABV8qAtocVmWvhEwSz7KkxAGOO5wAsWHVpX-8uwn1OCHOdIDQLLx0IxcEgFgDAc",
            "https://p52-caldav.icloud.com/published/2/MjAxMTg4NDQzMzQyMDExON96CchJBr3tDJgJsTIf_Pq7GNqvqHMiqbWgoek6GapG1i37t0ONPIu3-ecHw-d4sgLgfwbiJXiSsVHfU9iorfk",
            "https://p52-caldav.icloud.com/published/2/MjAxMTg4NDQzMzQyMDExON96CchJBr3tDJgJsTIf_Po1mX6PGsD0YmIKelfvmUCPq7XPVW3CzrjFBLzAN6_2AIonCjG6B5F6RI3Q2fsyqS0",
            "https://p52-caldav.icloud.com/published/2/MjAxMTg4NDQzMzQyMDExON96CchJBr3tDJgJsTIf_Po6c9xHM_YFem19LRQdkNz2IJfjt6ZnRvVhnj_Np_h1QedECmjyp0W59riZCmiMlI0",
            "https://p52-caldav.icloud.com/published/2/MjAxMTg4NDQzMzQyMDExON96CchJBr3tDJgJsTIf_PpDMdcxpUSPkf_v94X_Fht0Pn_gLQbi-ZBO85vVCENRkgmAJZNmaIv0RDlusP8Zmr0"
        ]
        
        # カレンダーごとの色設定
        self.calendar_colors = [
            "#3b82f6",  # 青
            "#ef4444",  # 赤
            "#10b981",  # 緑
            "#f59e0b",  # オレンジ
            "#8b5cf6"   # 紫
        ]
        
        # キャッシュ設定
        self.cache_dir = "/tmp/calendar_cache"
        self.cache_duration = 300  # 5分間キャッシュ
        self._ensure_cache_dir()
        
        # HTTPセッション設定
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AmbientPanel/1.0',
            'Accept': 'text/calendar, application/calendar+json'
        })
        
        # タイムアウト設定（短縮）
        self.timeout = 10  # 10秒に短縮

    def _ensure_cache_dir(self):
        """キャッシュディレクトリを作成"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_key(self, url: str, start_date: datetime, end_date: datetime) -> str:
        """キャッシュキーを生成"""
        key_data = f"{url}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        return f"calendar_{hash(key_data)}.json"

    def _is_cache_valid(self, cache_file: str) -> bool:
        """キャッシュが有効かチェック"""
        if not os.path.exists(cache_file):
            return False
        
        cache_time = os.path.getmtime(cache_file)
        current_time = datetime.now().timestamp()
        return (current_time - cache_time) < self.cache_duration

    def _load_from_cache(self, cache_file: str) -> Optional[List[Dict[str, Any]]]:
        """キャッシュからデータを読み込み"""
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return None

    def _save_to_cache(self, cache_file: str, data: List[Dict[str, Any]]):
        """データをキャッシュに保存"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    async def fetch_calendar_data(self, url: str) -> Optional[Calendar]:
        """iCloudカレンダーからiCalデータを取得（並列処理対応）"""
        try:
            logger.info(f"Fetching calendar data from: {url}")
            
            # aiohttpを使用して並列処理
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers={
                    'User-Agent': 'AmbientPanel/1.0',
                    'Accept': 'text/calendar, application/calendar+json'
                }
            ) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        text = await response.text()
                        calendar = Calendar.from_ical(text)
                        logger.info(f"Successfully parsed calendar with {len(calendar.walk('VEVENT'))} events")
                        return calendar
                    else:
                        logger.error(f"HTTP {response.status} for {url}")
                        return None
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching calendar data from {url}")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch calendar data from {url}: {e}")
            return None

    def parse_event(self, event, calendar_index: int) -> Optional[Dict[str, Any]]:
        """iCalイベントを辞書形式に変換"""
        try:
            # 基本情報を取得
            summary = str(event.get('summary', ''))
            description = str(event.get('description', ''))
            location = str(event.get('location', ''))
            
            # 開始・終了時間を取得
            dtstart = event.get('dtstart')
            dtend = event.get('dtend')
            
            if not dtstart:
                return None
                
            # 日時を文字列に変換
            start_str = self._format_datetime(dtstart)
            end_str = self._format_datetime(dtend) if dtend else start_str
            
            # イベントIDを生成
            uid = str(event.get('uid', f"{calendar_index}_{summary}_{start_str}"))
            
            return {
                'id': uid,
                'title': summary,
                'start': start_str,
                'end': end_str,
                'location': location,
                'description': description,
                'color': self.calendar_colors[calendar_index % len(self.calendar_colors)],
                'calendar_index': calendar_index,
                'all_day': self._is_all_day_event(dtstart, dtend)
            }
            
        except Exception as e:
            logger.error(f"Failed to parse event: {e}")
            return None

    def _format_datetime(self, dt_value) -> str:
        """iCal日時値を日本時間のISO文字列に変換"""
        jst = pytz.timezone('Asia/Tokyo')
        
        if hasattr(dt_value, 'dt'):
            # datetimeオブジェクトの場合
            dt = dt_value.dt
            if isinstance(dt, datetime):
                # タイムゾーン情報がない場合は日本時間として扱う
                if dt.tzinfo is None:
                    dt = jst.localize(dt)
                else:
                    # 他のタイムゾーンの場合は日本時間に変換
                    dt = dt.astimezone(jst)
                return dt.strftime('%Y-%m-%dT%H:%M:%S')
            else:
                # 日付のみの場合（終日イベント）
                return dt.strftime('%Y-%m-%dT00:00:00')
        else:
            # 文字列の場合
            try:
                parsed_dt = date_parser.parse(str(dt_value))
                if parsed_dt.tzinfo is None:
                    # タイムゾーン情報がない場合は日本時間として扱う
                    parsed_dt = jst.localize(parsed_dt)
                else:
                    # 他のタイムゾーンの場合は日本時間に変換
                    parsed_dt = parsed_dt.astimezone(jst)
                return parsed_dt.strftime('%Y-%m-%dT%H:%M:%S')
            except:
                return str(dt_value)

    def _is_all_day_event(self, dtstart, dtend) -> bool:
        """終日イベントかどうかを判定"""
        try:
            if hasattr(dtstart, 'dt') and hasattr(dtend, 'dt'):
                start_dt = dtstart.dt
                end_dt = dtend.dt
                
                # 日付のみの場合は終日イベント
                if not isinstance(start_dt, datetime) and not isinstance(end_dt, datetime):
                    return True
                    
                # 時間が00:00:00の場合は終日イベントの可能性
                if isinstance(start_dt, datetime) and isinstance(end_dt, datetime):
                    if (start_dt.hour == 0 and start_dt.minute == 0 and start_dt.second == 0 and
                        end_dt.hour == 0 and end_dt.minute == 0 and end_dt.second == 0):
                        return True
                        
        except Exception:
            pass
            
        return False

    async def get_all_events(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """すべてのカレンダーからイベントを取得して統合（キャッシュ対応）"""
        # デフォルトの日付範囲を設定
        if not start_date:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if not end_date:
            end_date = start_date + timedelta(days=365)  # 1年後まで
        
        # キャッシュキーを生成
        cache_key = f"all_events_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
        cache_file = os.path.join(self.cache_dir, cache_key)
        
        # キャッシュから読み込みを試行
        if self._is_cache_valid(cache_file):
            cached_data = self._load_from_cache(cache_file)
            if cached_data:
                logger.info(f"Loaded {len(cached_data)} events from cache")
                return cached_data
        
        logger.info(f"Fetching events from {len(self.calendar_urls)} calendars")
        
        # 並列処理でカレンダーデータを取得
        tasks = []
        for i, url in enumerate(self.calendar_urls):
            task = self._fetch_and_process_calendar(url, i, start_date, end_date)
            tasks.append(task)
        
        # すべてのタスクを並列実行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_events = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing calendar {i+1}: {result}")
                continue
            if result:
                all_events.extend(result)
                logger.info(f"Calendar {i+1}: {len(result)} events extracted")
        
        # イベントを開始時間でソート
        all_events.sort(key=lambda x: x['start'])
        
        # キャッシュに保存
        self._save_to_cache(cache_file, all_events)
        
        logger.info(f"Total events collected: {len(all_events)}")
        return all_events

    async def _fetch_and_process_calendar(self, url: str, calendar_index: int, 
                                        start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """カレンダーを取得して処理"""
        try:
            calendar = await self.fetch_calendar_data(url)
            if calendar:
                return self._extract_events_from_calendar(calendar, calendar_index, start_date, end_date)
            return []
        except Exception as e:
            logger.error(f"Error processing calendar {calendar_index+1}: {e}")
            return []

    def _extract_events_from_calendar(self, calendar: Calendar, calendar_index: int, 
                                    start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """カレンダーからイベントを抽出"""
        events = []
        
        for component in calendar.walk('VEVENT'):
            event = self.parse_event(component, calendar_index)
            if event:
                # 日付範囲内のイベントのみを追加
                event_start = self._parse_datetime_string(event['start'])
                if event_start and start_date <= event_start <= end_date:
                    events.append(event)
                    
        return events

    def _parse_datetime_string(self, dt_str: str) -> Optional[datetime]:
        """日時文字列をdatetimeオブジェクトに変換"""
        try:
            return date_parser.parse(dt_str)
        except:
            return None

    async def get_month_events(self, year: int, month: int) -> List[Dict[str, Any]]:
        """指定された月のイベントを取得"""
        from calendar import monthrange
        
        # 月の最初の日と最後の日を取得
        first_day = datetime(year, month, 1)
        last_day_num = monthrange(year, month)[1]
        last_day = datetime(year, month, last_day_num, 23, 59, 59)
        
        return await self.get_all_events(first_day, last_day)

    async def get_day_events(self, year: int, month: int, day: int) -> List[Dict[str, Any]]:
        """指定された日のイベントを取得"""
        start_date = datetime(year, month, day, 0, 0, 0)
        end_date = datetime(year, month, day, 23, 59, 59)
        
        return await self.get_all_events(start_date, end_date)

    async def get_today_events(self) -> List[Dict[str, Any]]:
        """今日のイベントを取得"""
        today = datetime.now()
        return await self.get_day_events(today.year, today.month, today.day)
