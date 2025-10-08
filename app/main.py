"""
Ambient Panel - 多機能情報パネル
メインアプリケーションエントリーポイント
"""

import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api import environment, spotify, weather, calendar, news
from app.services.hardware_detection import detect_environment

# 環境変数の読み込み
load_dotenv()

# 環境の検出
IS_RASPBERRY_PI = detect_environment()

app = FastAPI(
    title="Ambient Panel",
    description="Raspberry Pi搭載 多機能情報パネル",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイルの設定（Svelteビルドファイル用）
import os
if os.path.exists("frontend/dist"):
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")
else:
    # 開発環境では空のディレクトリを作成
    os.makedirs("frontend/dist", exist_ok=True)
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

# APIルーターの登録
app.include_router(environment.router, prefix="/api/environment", tags=["environment"])
app.include_router(spotify.router, prefix="/api/spotify", tags=["spotify"])
app.include_router(weather.router, prefix="/api/weather", tags=["weather"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(news.router, prefix="/api/news", tags=["news"])

@app.get("/")
async def root():
    """Svelteアプリケーションの提供"""
    from fastapi.responses import FileResponse
    return FileResponse("frontend/dist/index.html")

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy",
        "environment": "raspberry_pi" if IS_RASPBERRY_PI else "development",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
