"""
ニュースAPIエンドポイント
NewsAPI.orgを使用してニュース情報を取得
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
import os
import requests
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# ニュースAPIの設定
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

@router.get("/headlines")
async def get_news_headlines() -> Dict[str, Any]:
    """
    最新のニュースヘッドラインを取得
    
    Returns:
        Dict[str, Any]: ニュースヘッドライン一覧
    """
    if not NEWS_API_KEY:
        logger.warning("News API key not configured")
        return {
            "success": False,
            "error": "ニュースAPIキーが設定されていません",
            "data": {
                "articles": [],
                "total_results": 0
            }
        }
    
    try:
        # NewsAPI.orgからトップヘッドラインを取得
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": "jp",  # 日本のニュース
            "apiKey": NEWS_API_KEY,
            "pageSize": 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        articles = []
        for article in data.get("articles", []):
            articles.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
                "source": article.get("source", {}).get("name", ""),
                "image_url": article.get("urlToImage", "")
            })
        
        return {
            "success": True,
            "data": {
                "articles": articles,
                "total_results": data.get("totalResults", 0)
            },
            "source": "api"
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch news data: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/category/{category}")
async def get_news_by_category(category: str) -> Dict[str, Any]:
    """
    カテゴリ別のニュースを取得
    
    Args:
        category: ニュースカテゴリ（business, entertainment, health, science, sports, technology）
    
    Returns:
        Dict[str, Any]: カテゴリ別ニュース一覧
    """
    if not NEWS_API_KEY:
        logger.warning("News API key not configured, returning mock data")
        return {
            "success": True,
            "data": {
                "articles": [
                    {
                        "title": f"{category}のサンプルニュース",
                        "description": f"これは{category}カテゴリのサンプルニュースです。",
                        "url": f"https://example.com/{category}/news1",
                        "published_at": datetime.now().isoformat(),
                        "source": "サンプルニュース"
                    }
                ],
                "category": category,
                "total_results": 1
            },
            "source": "mock"
        }
    
    try:
        # NewsAPI.orgからカテゴリ別ニュースを取得
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": "jp",
            "category": category,
            "apiKey": NEWS_API_KEY,
            "pageSize": 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        articles = []
        for article in data.get("articles", []):
            articles.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
                "source": article.get("source", {}).get("name", ""),
                "image_url": article.get("urlToImage", "")
            })
        
        return {
            "success": True,
            "data": {
                "articles": articles,
                "category": category,
                "total_results": data.get("totalResults", 0)
            },
            "source": "api"
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news data for category {category}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch news data: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
