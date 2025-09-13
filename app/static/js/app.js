/**
 * Ambient Panel - 多機能情報パネル
 * メインJavaScriptアプリケーション
 */

class AmbientPanel {
    constructor() {
        this.currentTab = 'spotify';
        this.timer = null;
        this.pdtimer = null;
        this.pdtimerPhase = 'work'; // 'work' or 'break'
        this.pdtimerSessions = 0;
        this.updateInterval = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startDataUpdates();
        this.updateDateTime();
        this.loadInitialData();
    }

    setupEventListeners() {
        // タブナビゲーション
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Spotify コントロール
        document.getElementById('play-pause-btn').addEventListener('click', () => {
            this.togglePlayback();
        });
        document.getElementById('prev-btn').addEventListener('click', () => {
            this.previousTrack();
        });
        document.getElementById('next-btn').addEventListener('click', () => {
            this.nextTrack();
        });

        // タイマーコントロール
        document.getElementById('timer-start').addEventListener('click', () => {
            this.startTimer();
        });
        document.getElementById('timer-pause').addEventListener('click', () => {
            this.pauseTimer();
        });
        document.getElementById('timer-reset').addEventListener('click', () => {
            this.resetTimer();
        });

        // タイマープリセット
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setTimerPreset(parseInt(e.target.dataset.minutes));
            });
        });

        // ポモドーロタイマーコントロール
        document.getElementById('pdtimer-start').addEventListener('click', () => {
            this.startPDTimer();
        });
        document.getElementById('pdtimer-pause').addEventListener('click', () => {
            this.pausePDTimer();
        });
        document.getElementById('pdtimer-reset').addEventListener('click', () => {
            this.resetPDTimer();
        });

        // 仮想キーボード
        document.getElementById('keyboard-close').addEventListener('click', () => {
            this.hideVirtualKeyboard();
        });

        // テキスト入力フィールドで仮想キーボードを表示
        document.addEventListener('focusin', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                this.showVirtualKeyboard();
            }
        });
    }

    switchTab(tabName) {
        // タブボタンの状態更新
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // コンテンツの表示切り替え
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-content`).classList.add('active');

        this.currentTab = tabName;

        // タブ固有のデータを読み込み
        this.loadTabData(tabName);
    }

    async loadTabData(tabName) {
        switch (tabName) {
            case 'spotify':
                await this.loadPlaylists();
                break;
            case 'calendar':
                await this.loadCalendarEvents();
                break;
            case 'news':
                await this.loadNews();
                break;
        }
    }

    async loadInitialData() {
        await Promise.all([
            this.loadEnvironmentData(),
            this.loadWeatherData(),
            this.loadSpotifyStatus(),
            this.loadPlaylists(),
            this.loadCalendarEvents(),
            this.loadNews()
        ]);
    }

    startDataUpdates() {
        // 定期的なデータ更新
        this.updateInterval = setInterval(() => {
            this.updateDateTime();
            this.loadEnvironmentData();
            this.loadWeatherData();
            this.loadSpotifyStatus();
        }, 30000); // 30秒ごと

        // より頻繁な更新（環境データ）
        setInterval(() => {
            this.loadEnvironmentData();
        }, 10000); // 10秒ごと
    }

    updateDateTime() {
        const now = new Date();
        const dateStr = now.toLocaleDateString('ja-JP', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
        const timeStr = now.toLocaleTimeString('ja-JP', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        document.getElementById('current-date').textContent = dateStr;
        document.getElementById('current-time').textContent = timeStr;
    }

    async loadEnvironmentData() {
        try {
            const response = await fetch('/api/environment/');
            const data = await response.json();
            
            if (data.success) {
                const env = data.data;
                document.getElementById('indoor-temp').textContent = `${env.temperature}°C`;
                document.getElementById('indoor-humidity').textContent = `${env.humidity}%`;
                document.getElementById('indoor-co2').textContent = `${env.co2} ppm`;
            }
        } catch (error) {
            console.error('環境データの取得に失敗:', error);
        }
    }

    async loadWeatherData() {
        try {
            const response = await fetch('/api/weather/current');
            const data = await response.json();
            
            if (data.success) {
                const weather = data.data;
                document.getElementById('weather-temp').textContent = `${weather.temperature}°C`;
                document.getElementById('weather-location').textContent = weather.location;
                document.getElementById('weather-desc').textContent = weather.description;
                
                // 天気アイコンの更新
                const iconMap = {
                    '01d': 'fas fa-sun',
                    '01n': 'fas fa-moon',
                    '02d': 'fas fa-cloud-sun',
                    '02n': 'fas fa-cloud-moon',
                    '03d': 'fas fa-cloud',
                    '03n': 'fas fa-cloud',
                    '04d': 'fas fa-cloud',
                    '04n': 'fas fa-cloud',
                    '09d': 'fas fa-cloud-rain',
                    '09n': 'fas fa-cloud-rain',
                    '10d': 'fas fa-cloud-sun-rain',
                    '10n': 'fas fa-cloud-moon-rain',
                    '11d': 'fas fa-bolt',
                    '11n': 'fas fa-bolt',
                    '13d': 'fas fa-snowflake',
                    '13n': 'fas fa-snowflake',
                    '50d': 'fas fa-smog',
                    '50n': 'fas fa-smog'
                };
                
                const iconClass = iconMap[weather.icon] || 'fas fa-sun';
                document.getElementById('weather-icon').className = iconClass;
            }
        } catch (error) {
            console.error('天気データの取得に失敗:', error);
        }
    }

    async loadSpotifyStatus() {
        try {
            const response = await fetch('/api/spotify/current');
            const data = await response.json();
            
            if (data.success && data.is_playing) {
                const track = data.track;
                document.getElementById('track-name').textContent = track.name;
                document.getElementById('artist-name').textContent = track.artist;
                document.getElementById('album-art').src = track.image_url;
                
                // プログレスバーの更新
                const progress = (track.progress_ms / track.duration_ms) * 100;
                document.getElementById('progress-bar').style.width = `${progress}%`;
                
                // 再生ボタンの状態更新
                const playBtn = document.getElementById('play-pause-btn');
                const icon = playBtn.querySelector('i');
                icon.className = 'fas fa-pause';
            } else {
                // 再生停止状態
                const playBtn = document.getElementById('play-pause-btn');
                const icon = playBtn.querySelector('i');
                icon.className = 'fas fa-play';
            }
        } catch (error) {
            console.error('Spotify状態の取得に失敗:', error);
        }
    }

    async loadPlaylists() {
        try {
            const response = await fetch('/api/spotify/playlists');
            const data = await response.json();
            
            if (data.success) {
                const container = document.getElementById('playlist-grid');
                container.innerHTML = '';
                
                data.playlists.forEach(playlist => {
                    const item = document.createElement('div');
                    item.className = 'playlist-item';
                    item.innerHTML = `
                        <img src="${playlist.image_url}" alt="${playlist.name}">
                        <h3>${playlist.name}</h3>
                        <p>${playlist.track_count}曲</p>
                    `;
                    item.addEventListener('click', () => {
                        this.selectPlaylist(playlist.id);
                    });
                    container.appendChild(item);
                });
            }
        } catch (error) {
            console.error('プレイリストの取得に失敗:', error);
        }
    }

    async loadCalendarEvents() {
        try {
            const response = await fetch('/api/calendar/today');
            const data = await response.json();
            
            if (data.success) {
                const container = document.getElementById('calendar-events');
                container.innerHTML = '';
                
                if (data.data.events.length === 0) {
                    container.innerHTML = '<p>今日の予定はありません</p>';
                    return;
                }
                
                data.data.events.forEach(event => {
                    const item = document.createElement('div');
                    item.className = 'event-item';
                    item.innerHTML = `
                        <h3>${event.title}</h3>
                        <div class="time">${this.formatTime(event.start)} - ${this.formatTime(event.end)}</div>
                        ${event.location ? `<div class="location">${event.location}</div>` : ''}
                    `;
                    container.appendChild(item);
                });
            }
        } catch (error) {
            console.error('カレンダー予定の取得に失敗:', error);
        }
    }

    async loadNews() {
        try {
            const response = await fetch('/api/news/headlines');
            const data = await response.json();
            
            if (data.success) {
                const container = document.getElementById('news-list');
                container.innerHTML = '';
                
                data.data.articles.forEach(article => {
                    const item = document.createElement('div');
                    item.className = 'news-item';
                    item.innerHTML = `
                        <h3>${article.title}</h3>
                        <p>${article.description}</p>
                        <div class="source">${article.source}</div>
                    `;
                    item.addEventListener('click', () => {
                        window.open(article.url, '_blank');
                    });
                    container.appendChild(item);
                });
            }
        } catch (error) {
            console.error('ニュースの取得に失敗:', error);
        }
    }

    // Spotify コントロール
    async togglePlayback() {
        try {
            const response = await fetch('/api/spotify/play', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                this.loadSpotifyStatus();
            }
        } catch (error) {
            console.error('再生制御に失敗:', error);
        }
    }

    async previousTrack() {
        try {
            await fetch('/api/spotify/previous', { method: 'POST' });
            this.loadSpotifyStatus();
        } catch (error) {
            console.error('前の曲への切り替えに失敗:', error);
        }
    }

    async nextTrack() {
        try {
            await fetch('/api/spotify/next', { method: 'POST' });
            this.loadSpotifyStatus();
        } catch (error) {
            console.error('次の曲への切り替えに失敗:', error);
        }
    }

    async selectPlaylist(playlistId) {
        // TODO: プレイリストの選択と再生
        console.log('プレイリスト選択:', playlistId);
    }

    // タイマー機能
    startTimer() {
        if (this.timer) {
            clearInterval(this.timer);
        }
        
        let seconds = this.getTimerSeconds();
        this.timer = setInterval(() => {
            seconds--;
            this.updateTimerDisplay(seconds);
            
            if (seconds <= 0) {
                this.resetTimer();
                this.showNotification('タイマーが終了しました！');
            }
        }, 1000);
    }

    pauseTimer() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    resetTimer() {
        this.pauseTimer();
        this.updateTimerDisplay(0);
    }

    setTimerPreset(minutes) {
        this.updateTimerDisplay(minutes * 60);
    }

    getTimerSeconds() {
        const display = document.getElementById('timer-display').textContent;
        const parts = display.split(':');
        return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2]);
    }

    updateTimerDisplay(totalSeconds) {
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        
        document.getElementById('timer-display').textContent = 
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    // ポモドーロタイマー機能
    startPDTimer() {
        if (this.pdtimer) {
            clearInterval(this.pdtimer);
        }
        
        let seconds = this.getPDTimerSeconds();
        this.pdtimer = setInterval(() => {
            seconds--;
            this.updatePDTimerDisplay(seconds);
            
            if (seconds <= 0) {
                this.switchPDTimerPhase();
            }
        }, 1000);
    }

    pausePDTimer() {
        if (this.pdtimer) {
            clearInterval(this.pdtimer);
            this.pdtimer = null;
        }
    }

    resetPDTimer() {
        this.pausePDTimer();
        this.pdtimerPhase = 'work';
        this.pdtimerSessions = 0;
        this.updatePDTimerDisplay(25 * 60);
        this.updatePDTimerStatus();
    }

    switchPDTimerPhase() {
        this.pausePDTimer();
        
        if (this.pdtimerPhase === 'work') {
            this.pdtimerPhase = 'break';
            this.pdtimerSessions++;
            this.updatePDTimerDisplay(5 * 60); // 5分休憩
            this.showNotification('作業時間終了！休憩時間です。');
        } else {
            this.pdtimerPhase = 'work';
            this.updatePDTimerDisplay(25 * 60); // 25分作業
            this.showNotification('休憩時間終了！作業を再開しましょう。');
        }
        
        this.updatePDTimerStatus();
        
        if (this.pdtimerSessions < 4) {
            this.startPDTimer();
        }
    }

    getPDTimerSeconds() {
        const display = document.getElementById('pdtimer-display').textContent;
        const parts = display.split(':');
        return parseInt(parts[0]) * 60 + parseInt(parts[1]);
    }

    updatePDTimerDisplay(totalSeconds) {
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        
        document.getElementById('pdtimer-display').textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    updatePDTimerStatus() {
        const status = this.pdtimerPhase === 'work' ? '作業時間' : '休憩時間';
        document.getElementById('pdtimer-status').textContent = status;
        document.getElementById('session-count').textContent = this.pdtimerSessions;
    }

    // 仮想キーボード
    showVirtualKeyboard() {
        document.getElementById('virtual-keyboard').style.display = 'block';
    }

    hideVirtualKeyboard() {
        document.getElementById('virtual-keyboard').style.display = 'none';
    }

    // ユーティリティ関数
    formatTime(timeString) {
        const date = new Date(timeString);
        return date.toLocaleTimeString('ja-JP', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    showNotification(message) {
        // 簡単な通知表示（実際の実装ではより洗練された通知システムを使用）
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #667eea;
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            z-index: 10000;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// アプリケーションの初期化
document.addEventListener('DOMContentLoaded', () => {
    new AmbientPanel();
});
