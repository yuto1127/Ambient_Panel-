"""
Calendar APIエンドポイント
iCloudカレンダーから予定情報を取得
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
import os
from datetime import datetime, timedelta
import calendar
from app.services.icloud_calendar import ICloudCalendarService

router = APIRouter()
logger = logging.getLogger(__name__)

# iCloudカレンダーサービスを初期化
icloud_service = ICloudCalendarService()

@router.get("/events")
async def get_calendar_events() -> Dict[str, Any]:
    """
    直近のカレンダー予定を取得
    
    Returns:
        Dict[str, Any]: カレンダー予定一覧
    """
    # TODO: Google Calendar APIを使用して予定を取得
    # 現在はモックデータを返す
    
    mock_events = [
        {
            "id": "event_1",
            "title": "会議",
            "start": "2024-01-01T10:00:00",
            "end": "2024-01-01T11:00:00",
            "location": "会議室A",
            "description": "プロジェクト会議"
        },
        {
            "id": "event_2",
            "title": "ランチ",
            "start": "2024-01-01T12:00:00",
            "end": "2024-01-01T13:00:00",
            "location": "レストラン",
            "description": "チームランチ"
        }
    ]
    
    return {
        "success": True,
        "data": {
            "events": mock_events,
            "count": len(mock_events)
        },
        "source": "mock"
    }

@router.get("/today")
async def get_today_events() -> Dict[str, Any]:
    """
    今日の予定を取得
    
    Returns:
        Dict[str, Any]: 今日の予定一覧
    """
    try:
        logger.info("Fetching today's events from iCloud calendars")
        events = await icloud_service.get_today_events()
        
        # 日本時間（JST）で今日の日付を取得
        import pytz
        jst = pytz.timezone('Asia/Tokyo')
        today_jst = datetime.now(jst)
        
        return {
            "success": True,
            "data": {
                "events": events,
                "date": today_jst.strftime("%Y-%m-%d"),
                "count": len(events)
            },
            "source": "icloud"
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch today's events: {e}")
        # エラー時はモックデータを返す（日本時間使用）
        import pytz
        jst = pytz.timezone('Asia/Tokyo')
        today_jst = datetime.now(jst)
        today_str = today_jst.strftime("%Y-%m-%d")
        
        mock_events = [
            {
                "id": "fallback_event_1",
                "title": "カレンダー接続エラー",
                "start": f"{today_str}T09:00:00",
                "end": f"{today_str}T10:00:00",
                "location": "システム",
                "description": "iCloudカレンダーへの接続に失敗しました",
                "color": "#ef4444"
            }
        ]
        
        return {
            "success": False,
            "data": {
                "events": mock_events,
                "date": today_str,
                "count": len(mock_events)
            },
            "source": "fallback",
            "error": str(e)
        }

@router.get("/month/{year}/{month}")
async def get_month_events(year: int, month: int) -> Dict[str, Any]:
    """
    指定された月の予定を取得
    
    Args:
        year: 年
        month: 月 (1-12)
    
    Returns:
        Dict[str, Any]: 月の予定一覧
    """
    try:
        # 月の妥当性チェック
        if month < 1 or month > 12:
            raise HTTPException(status_code=400, detail="月は1-12の範囲で指定してください")
        
        logger.info(f"Fetching events for {year}-{month} from iCloud calendars")
        events = await icloud_service.get_month_events(year, month)
        
        # 月の最初の日と最後の日を取得
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, calendar.monthrange(year, month)[1])
        
        return {
            "success": True,
            "data": {
                "events": events,
                "year": year,
                "month": month,
                "first_day": first_day.strftime("%Y-%m-%d"),
                "last_day": last_day.strftime("%Y-%m-%d"),
                "count": len(events)
            },
            "source": "icloud"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"無効な日付です: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to fetch month events for {year}-{month}: {e}")
        # エラー時はモックデータを返す
        mock_events = generate_mock_month_events(year, month)
        
        return {
            "success": False,
            "data": {
                "events": mock_events,
                "year": year,
                "month": month,
                "first_day": datetime(year, month, 1).strftime("%Y-%m-%d"),
                "last_day": datetime(year, month, calendar.monthrange(year, month)[1]).strftime("%Y-%m-%d"),
                "count": len(mock_events)
            },
            "source": "fallback",
            "error": str(e)
        }

@router.get("/day/{year}/{month}/{day}")
async def get_day_events(year: int, month: int, day: int) -> Dict[str, Any]:
    """
    指定された日の予定を取得
    
    Args:
        year: 年
        month: 月 (1-12)
        day: 日
    
    Returns:
        Dict[str, Any]: 日の予定一覧
    """
    try:
        # 日付の妥当性チェック
        target_date = datetime(year, month, day)
        
        logger.info(f"Fetching events for {year}-{month}-{day} from iCloud calendars")
        events = await icloud_service.get_day_events(year, month, day)
        
        return {
            "success": True,
            "data": {
                "events": events,
                "date": target_date.strftime("%Y-%m-%d"),
                "count": len(events)
            },
            "source": "icloud"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"無効な日付です: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to fetch day events for {year}-{month}-{day}: {e}")
        # エラー時はモックデータを返す
        mock_events = generate_mock_day_events(year, month, day)
        
        return {
            "success": False,
            "data": {
                "events": mock_events,
                "date": datetime(year, month, day).strftime("%Y-%m-%d"),
                "count": len(mock_events)
            },
            "source": "fallback",
            "error": str(e)
        }

def generate_mock_month_events(year: int, month: int) -> List[Dict[str, Any]]:
    """月のモックイベントを生成"""
    events = []
    colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
    
    # 月の日数を取得
    days_in_month = calendar.monthrange(year, month)[1]
    
    # ランダムにイベントを生成
    import random
    random.seed(year * 100 + month)  # 同じ月は同じイベントを生成
    
    # 祝日データを追加（2025年の祝日）
    holidays_2025 = {
        1: [1],  # 元日
        2: [11, 12],  # 建国記念の日、建国記念の日振替休日
        3: [20],  # 春分の日
        4: [29],  # 昭和の日
        5: [3, 4, 5, 6],  # 憲法記念日、みどりの日、こどもの日、こどもの日振替休日
        7: [21],  # 海の日
        8: [11],  # 山の日
        9: [15, 22, 23],  # 敬老の日、秋分の日、秋分の日振替休日
        10: [13, 14],  # スポーツの日、スポーツの日振替休日
        11: [3, 23],  # 文化の日、勤労感謝の日
        12: [23]  # 天皇誕生日
    }
    
    holiday_names = {
        1: "元日",
        2: "建国記念の日",
        3: "春分の日", 
        4: "昭和の日",
        5: ["憲法記念日", "みどりの日", "こどもの日"],
        7: "海の日",
        8: "山の日",
        9: ["敬老の日", "秋分の日"],
        10: "スポーツの日",
        11: ["文化の日", "勤労感謝の日"],
        12: "天皇誕生日"
    }
    
    for day in range(1, days_in_month + 1):
        # 祝日を追加
        if month in holidays_2025 and day in holidays_2025[month]:
            holiday_name = holiday_names[month]
            if isinstance(holiday_name, list):
                # 複数の祝日がある場合（5月、9月、11月）
                holiday_index = holidays_2025[month].index(day)
                holiday_name = holiday_name[holiday_index] if holiday_index < len(holiday_name) else holiday_name[0]
            
            events.append({
                "id": f"holiday_{year}_{month}_{day}",
                "title": holiday_name,
                "start": f"{year}-{month:02d}-{day:02d}",
                "end": f"{year}-{month:02d}-{day:02d}",
                "all_day": True,
                "location": "",
                "description": f"日本の祝日: {holiday_name}",
                "color": "#ff6b6b",
                "source": "japanese_holidays"
            })
        
        # 終日イベントを追加（10%の確率）
        if random.random() < 0.1:
            all_day_titles = [
                "会社休業日", "研修日", "イベント開催日", "記念日",
                "特別休暇", "メンテナンス日", "システム停止日"
            ]
            
            events.append({
                "id": f"allday_{year}_{month}_{day}",
                "title": random.choice(all_day_titles),
                "start": f"{year}-{month:02d}-{day:02d}T00:00:00",
                "end": f"{year}-{month:02d}-{day:02d}T23:59:59",
                "all_day": True,
                "location": "",
                "description": f"{random.choice(all_day_titles)}の詳細",
                "color": "#8b5cf6",
                "source": "icloud"
            })
        
        # 通常の時間指定イベントを生成（30%の確率）
        if random.random() < 0.3:
            num_events = random.randint(1, 3)
            for i in range(num_events):
                hour = random.randint(9, 17)
                minute = random.choice([0, 15, 30, 45])
                duration = random.choice([30, 60, 90, 120])
                
                start_time = datetime(year, month, day, hour, minute)
                end_time = start_time + timedelta(minutes=duration)
                
                event_titles = [
                    "会議", "ランチ", "プロジェクトレビュー", "コードレビュー",
                    "チームミーティング", "1on1", "プレゼンテーション", "研修",
                    "面談", "打ち合わせ", "デモ", "計画会議"
                ]
                
                event_locations = [
                    "会議室A", "会議室B", "会議室C", "レストラン", "リモート",
                    "オフィス", "カフェ", "ホテル", "展示会場"
                ]
                
                events.append({
                    "id": f"event_{year}_{month}_{day}_{i}",
                    "title": random.choice(event_titles),
                    "start": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "location": random.choice(event_locations),
                    "description": f"{random.choice(event_titles)}の詳細",
                    "color": random.choice(colors),
                    "source": "icloud"
                })
    
    return events

def generate_mock_day_events(year: int, month: int, day: int) -> List[Dict[str, Any]]:
    """日のモックイベントを生成"""
    target_date = datetime(year, month, day)
    today = datetime.now()
    
    events = []
    colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
    
    # 祝日データを追加（2025年の祝日）
    holidays_2025 = {
        1: [1],  # 元日
        2: [11, 12],  # 建国記念の日、建国記念の日振替休日
        3: [20],  # 春分の日
        4: [29],  # 昭和の日
        5: [3, 4, 5, 6],  # 憲法記念日、みどりの日、こどもの日、こどもの日振替休日
        7: [21],  # 海の日
        8: [11],  # 山の日
        9: [15, 22, 23],  # 敬老の日、秋分の日、秋分の日振替休日
        10: [13, 14],  # スポーツの日、スポーツの日振替休日
        11: [3, 23],  # 文化の日、勤労感謝の日
        12: [23]  # 天皇誕生日
    }
    
    holiday_names = {
        1: "元日",
        2: "建国記念の日",
        3: "春分の日", 
        4: "昭和の日",
        5: ["憲法記念日", "みどりの日", "こどもの日"],
        7: "海の日",
        8: "山の日",
        9: ["敬老の日", "秋分の日"],
        10: "スポーツの日",
        11: ["文化の日", "勤労感謝の日"],
        12: "天皇誕生日"
    }
    
    # 祝日を追加
    if month in holidays_2025 and day in holidays_2025[month]:
        holiday_name = holiday_names[month]
        if isinstance(holiday_name, list):
            # 複数の祝日がある場合（5月、9月、11月）
            holiday_index = holidays_2025[month].index(day)
            holiday_name = holiday_name[holiday_index] if holiday_index < len(holiday_name) else holiday_name[0]
        
        events.append({
            "id": f"holiday_{year}_{month}_{day}",
            "title": holiday_name,
            "start": f"{year}-{month:02d}-{day:02d}",
            "end": f"{year}-{month:02d}-{day:02d}",
            "all_day": True,
            "location": "",
            "description": f"日本の祝日: {holiday_name}",
            "color": "#ff6b6b",
            "source": "japanese_holidays"
        })
    
    # 今日の場合は既存のモックデータを使用
    if target_date.date() == today.date():
        events.extend([
            {
                "id": "today_event_1",
                "title": "朝のミーティング",
                "start": f"{target_date.strftime('%Y-%m-%d')}T09:00:00",
                "end": f"{target_date.strftime('%Y-%m-%d')}T10:00:00",
                "location": "会議室B",
                "description": "日次ミーティング",
                "color": "#3b82f6",
                "source": "icloud"
            },
            {
                "id": "today_event_2",
                "title": "プロジェクトレビュー",
                "start": f"{target_date.strftime('%Y-%m-%d')}T14:00:00",
                "end": f"{target_date.strftime('%Y-%m-%d')}T15:30:00",
                "location": "会議室A",
                "description": "四半期レビュー",
                "color": "#ef4444",
                "source": "icloud"
            }
        ])
        return events
    
    # 他の日はランダムに生成
    import random
    random.seed(year * 10000 + month * 100 + day)
    
    # 終日イベントを追加（20%の確率）
    if random.random() < 0.2:
        all_day_titles = [
            "会社休業日", "研修日", "イベント開催日", "記念日",
            "特別休暇", "メンテナンス日", "システム停止日"
        ]
        
        events.append({
            "id": f"allday_{year}_{month}_{day}",
            "title": random.choice(all_day_titles),
            "start": f"{year}-{month:02d}-{day:02d}T00:00:00",
            "end": f"{year}-{month:02d}-{day:02d}T23:59:59",
            "all_day": True,
            "location": "",
            "description": f"{random.choice(all_day_titles)}の詳細",
            "color": "#8b5cf6",
            "source": "icloud"
        })
    
    # 通常の時間指定イベントを生成（40%の確率）
    if random.random() < 0.4:
        num_events = random.randint(1, 2)
        for i in range(num_events):
            hour = random.randint(9, 17)
            minute = random.choice([0, 15, 30, 45])
            duration = random.choice([30, 60, 90])
            
            start_time = datetime(year, month, day, hour, minute)
            end_time = start_time + timedelta(minutes=duration)
            
            event_titles = [
                "会議", "ランチ", "プロジェクトレビュー", "コードレビュー",
                "チームミーティング", "1on1", "プレゼンテーション", "研修"
            ]
            
            event_locations = [
                "会議室A", "会議室B", "レストラン", "リモート", "オフィス"
            ]
            
            events.append({
                "id": f"event_{year}_{month}_{day}_{i}",
                "title": random.choice(event_titles),
                "start": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "end": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "location": random.choice(event_locations),
                "description": f"{random.choice(event_titles)}の詳細",
                "color": random.choice(colors),
                "source": "icloud"
            })
    
    return events
