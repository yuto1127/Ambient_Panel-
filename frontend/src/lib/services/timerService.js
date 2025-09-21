import { timer, pomodoroTimer, timerSettings } from '$lib/stores/timerStore.js';
import { get } from 'svelte/store';

class TimerService {
	constructor() {
		this.timerInterval = null;
		this.pomodoroInterval = null;
		this.isInitialized = false;
	}

	/**
	 * サービスを初期化
	 */
	initialize() {
		if (this.isInitialized) return;
		
		console.log('TimerService: 初期化中...');
		
		// ページの可視性変更を監視
		if (typeof document !== 'undefined') {
			document.addEventListener('visibilitychange', () => {
				if (!document.hidden) {
					this.syncTimers();
				}
			});
		}

		this.isInitialized = true;
		console.log('TimerService: 初期化完了');
	}

	/**
	 * 通常タイマーを開始
	 */
	startTimer() {
		const currentState = get(timer);
		
		if (currentState.seconds <= 0) {
			console.error('TimerService: タイマーを開始できません。時間を設定してください。');
			return false;
		}

		console.log('TimerService: 通常タイマーを開始');
		
		// 既存のタイマーを停止
		this.stopTimer();
		
		const now = Date.now();
		
		timer.update(state => ({
			...state,
			isRunning: true,
			isPaused: false,
			startTime: now,
			pauseTime: null
		}));

		// タイマーを開始
		this.timerInterval = setInterval(() => {
			this.updateTimer();
		}, 1000);

		return true;
	}

	/**
	 * 通常タイマーを停止
	 */
	stopTimer() {
		console.log('TimerService: 通常タイマーを停止');
		
		if (this.timerInterval) {
			clearInterval(this.timerInterval);
			this.timerInterval = null;
		}
		
		timer.update(state => ({
			...state,
			isRunning: false,
			isPaused: false,
			startTime: null,
			pauseTime: null
		}));
	}

	/**
	 * 通常タイマーを一時停止/再開
	 */
	pauseTimer() {
		const currentState = get(timer);
		
		if (currentState.isRunning && !currentState.isPaused) {
			console.log('TimerService: 通常タイマーを一時停止');
			
			// タイマーを停止
			if (this.timerInterval) {
				clearInterval(this.timerInterval);
				this.timerInterval = null;
			}
			
			timer.update(state => ({
				...state,
				isPaused: true,
				pauseTime: Date.now()
			}));
		} else if (currentState.isPaused) {
			console.log('TimerService: 通常タイマーを再開');
			
			// 一時停止時間を計算
			const pauseDuration = Date.now() - currentState.pauseTime;
			const newStartTime = currentState.startTime + pauseDuration;
			
			timer.update(state => ({
				...state,
				isPaused: false,
				startTime: newStartTime,
				pauseTime: null
			}));
			
			// タイマーを再開
			this.timerInterval = setInterval(() => {
				this.updateTimer();
			}, 1000);
		}
	}

	/**
	 * 通常タイマーをリセット
	 */
	resetTimer() {
		console.log('TimerService: 通常タイマーをリセット');
		
		this.stopTimer();
		
		timer.update(state => ({
			...state,
			seconds: state.totalSeconds,
			isRunning: false,
			isPaused: false,
			startTime: null,
			pauseTime: null
		}));
	}

	/**
	 * 通常タイマーに時間を設定
	 */
	setTimerTime(hours, minutes, seconds) {
		const totalSeconds = hours * 3600 + minutes * 60 + seconds;
		
		console.log(`TimerService: タイマー時間を設定: ${hours}時間${minutes}分${seconds}秒 (${totalSeconds}秒)`);
		
		timer.update(state => ({
			...state,
			seconds: totalSeconds,
			totalSeconds: totalSeconds,
			isRunning: false,
			isPaused: false,
			startTime: null,
			pauseTime: null
		}));
	}

	/**
	 * 通常タイマーを更新
	 */
	updateTimer() {
		const currentState = get(timer);
		
		if (!currentState.isRunning || currentState.isPaused) {
			return;
		}

		const now = Date.now();
		const elapsed = Math.floor((now - currentState.startTime) / 1000);
		const remainingSeconds = Math.max(0, currentState.totalSeconds - elapsed);
		
		if (remainingSeconds <= 0) {
			console.log('TimerService: 通常タイマー終了');
			
			timer.update(state => ({
				...state,
				seconds: 0,
				isRunning: false,
				isPaused: false
			}));
			
			this.stopTimer();
			this.notifyTimerComplete('timer');
		} else {
			timer.update(state => ({
				...state,
				seconds: remainingSeconds
			}));
		}
	}

	/**
	 * ポモドーロタイマーを開始
	 */
	startPomodoroTimer() {
		const currentState = get(pomodoroTimer);
		
		if (currentState.seconds <= 0) {
			console.error('TimerService: ポモドーロタイマーを開始できません。時間を設定してください。');
			return false;
		}

		console.log('TimerService: ポモドーロタイマーを開始');
		
		// 既存のタイマーを停止
		this.stopPomodoroTimer();
		
		const now = Date.now();
		
		pomodoroTimer.update(state => ({
			...state,
			isRunning: true,
			isPaused: false,
			startTime: now,
			pauseTime: null
		}));

		// タイマーを開始
		this.pomodoroInterval = setInterval(() => {
			this.updatePomodoroTimer();
		}, 1000);

		return true;
	}

	/**
	 * ポモドーロタイマーを停止
	 */
	stopPomodoroTimer() {
		console.log('TimerService: ポモドーロタイマーを停止');
		
		if (this.pomodoroInterval) {
			clearInterval(this.pomodoroInterval);
			this.pomodoroInterval = null;
		}
		
		pomodoroTimer.update(state => ({
			...state,
			isRunning: false,
			isPaused: false,
			startTime: null,
			pauseTime: null
		}));
	}

	/**
	 * ポモドーロタイマーを一時停止/再開
	 */
	pausePomodoroTimer() {
		const currentState = get(pomodoroTimer);
		
		if (currentState.isRunning && !currentState.isPaused) {
			console.log('TimerService: ポモドーロタイマーを一時停止');
			
			// タイマーを停止
			if (this.pomodoroInterval) {
				clearInterval(this.pomodoroInterval);
				this.pomodoroInterval = null;
			}
			
			pomodoroTimer.update(state => ({
				...state,
				isPaused: true,
				pauseTime: Date.now()
			}));
		} else if (currentState.isPaused) {
			console.log('TimerService: ポモドーロタイマーを再開');
			
			// 一時停止時間を計算
			const pauseDuration = Date.now() - currentState.pauseTime;
			const newStartTime = currentState.startTime + pauseDuration;
			
			pomodoroTimer.update(state => ({
				...state,
				isPaused: false,
				startTime: newStartTime,
				pauseTime: null
			}));
			
			// タイマーを再開
			this.pomodoroInterval = setInterval(() => {
				this.updatePomodoroTimer();
			}, 1000);
		}
	}

	/**
	 * ポモドーロタイマーをリセット
	 */
	resetPomodoroTimer() {
		console.log('TimerService: ポモドーロタイマーをリセット');
		
		this.stopPomodoroTimer();
		
		const settings = get(timerSettings);
		
		pomodoroTimer.update(state => ({
			...state,
			seconds: settings.workTime * 60,
			totalSeconds: settings.workTime * 60,
			phase: 'work',
			sessions: 0,
			isRunning: false,
			isPaused: false,
			startTime: null,
			pauseTime: null
		}));
	}

	/**
	 * ポモドーロタイマーの設定を更新
	 */
	updatePomodoroSettings(workTime, breakTime, longBreakTime, sessions) {
		console.log(`TimerService: ポモドーロ設定を更新: 作業${workTime}分, 休憩${breakTime}分, 長休憩${longBreakTime}分, セッション${sessions}回`);
		
		timerSettings.update(state => ({
			...state,
			workTime,
			breakTime,
			longBreakTime,
			sessions
		}));

		// 現在のタイマーをリセット
		this.resetPomodoroTimer();
	}

	/**
	 * ポモドーロタイマーを更新
	 */
	updatePomodoroTimer() {
		const currentState = get(pomodoroTimer);
		
		if (!currentState.isRunning || currentState.isPaused) {
			return;
		}

		const now = Date.now();
		const elapsed = Math.floor((now - currentState.startTime) / 1000);
		const remainingSeconds = Math.max(0, currentState.totalSeconds - elapsed);
		
		if (remainingSeconds <= 0) {
			console.log('TimerService: ポモドーロフェーズ終了');
			
			this.switchPomodoroPhase(currentState);
		} else {
			pomodoroTimer.update(state => ({
				...state,
				seconds: remainingSeconds
			}));
		}
	}

	/**
	 * ポモドーロタイマーのフェーズを切り替え
	 */
	switchPomodoroPhase(currentState) {
		const settings = get(timerSettings);
		
		if (currentState.phase === 'work') {
			// 作業時間終了 → 休憩時間
			const newSessions = currentState.sessions + 1;
			const isCompleted = newSessions >= settings.sessions;
			
			console.log(`TimerService: 作業時間終了 (セッション ${newSessions}/${settings.sessions})`);
			
			if (isCompleted) {
				// 全セッション完了
				pomodoroTimer.update(state => ({
					...state,
					seconds: 0,
					totalSeconds: 0,
					phase: 'completed',
					sessions: newSessions,
					isRunning: false,
					isPaused: false
				}));
				
				this.stopPomodoroTimer();
				this.notifyTimerComplete('pomodoro');
			} else {
				// 休憩時間に移行
				const breakDuration = newSessions % 4 === 0 ? settings.longBreakTime : settings.breakTime;
				const breakPhase = newSessions % 4 === 0 ? 'longBreak' : 'break';
				
				pomodoroTimer.update(state => ({
					...state,
					seconds: breakDuration * 60,
					totalSeconds: breakDuration * 60,
					phase: breakPhase,
					sessions: newSessions,
					isRunning: false,
					isPaused: false
				}));
				
				this.stopPomodoroTimer();
				
				// 休憩時間を自動開始
				setTimeout(() => {
					this.startPomodoroTimer();
				}, 1000);
			}
		} else {
			// 休憩時間終了 → 作業時間
			console.log('TimerService: 休憩時間終了 → 作業時間開始');
			
			pomodoroTimer.update(state => ({
				...state,
				seconds: settings.workTime * 60,
				totalSeconds: settings.workTime * 60,
				phase: 'work',
				isRunning: false,
				isPaused: false
			}));
			
			this.stopPomodoroTimer();
			
			// 作業時間を自動開始
			setTimeout(() => {
				this.startPomodoroTimer();
			}, 1000);
		}
	}

	/**
	 * タイマーを同期（ページが再表示された時）
	 */
	syncTimers() {
		const timerState = get(timer);
		const pomodoroState = get(pomodoroTimer);
		
		// 通常タイマーの同期
		if (timerState.isRunning && !timerState.isPaused && timerState.startTime) {
			const now = Date.now();
			const elapsed = Math.floor((now - timerState.startTime) / 1000);
			const remainingSeconds = Math.max(0, timerState.totalSeconds - elapsed);
			
			if (remainingSeconds <= 0) {
				this.stopTimer();
				this.notifyTimerComplete('timer');
			} else {
				timer.update(state => ({
					...state,
					seconds: remainingSeconds
				}));
			}
		}
		
		// ポモドーロタイマーの同期
		if (pomodoroState.isRunning && !pomodoroState.isPaused && pomodoroState.startTime) {
			const now = Date.now();
			const elapsed = Math.floor((now - pomodoroState.startTime) / 1000);
			const remainingSeconds = Math.max(0, pomodoroState.totalSeconds - elapsed);
			
			if (remainingSeconds <= 0) {
				this.switchPomodoroPhase(pomodoroState);
			} else {
				pomodoroTimer.update(state => ({
					...state,
					seconds: remainingSeconds
				}));
			}
		}
	}

	/**
	 * タイマー完了の通知
	 */
	notifyTimerComplete(type) {
		console.log(`TimerService: ${type}タイマー完了`);
		
		// ブラウザ通知を送信
		if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'granted') {
			const title = type === 'timer' ? 'タイマー完了' : 'ポモドーロ完了';
			const body = type === 'timer' ? '設定した時間が経過しました' : 'ポモドーロセッションが完了しました';
			
			new Notification(title, {
				body: body,
				icon: '/favicon.ico'
			});
		}
		
		// 音声通知
		this.playNotificationSound();
	}

	/**
	 * 通知音を再生
	 */
	playNotificationSound() {
		if (typeof window === 'undefined') {
			return;
		}
		
		try {
			const audioContext = new (window.AudioContext || window.webkitAudioContext)();
			const oscillator = audioContext.createOscillator();
			const gainNode = audioContext.createGain();
			
			oscillator.connect(gainNode);
			gainNode.connect(audioContext.destination);
			
			oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
			gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
			gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
			
			oscillator.start(audioContext.currentTime);
			oscillator.stop(audioContext.currentTime + 0.5);
		} catch (error) {
			console.log('TimerService: 音声通知の再生に失敗:', error);
		}
	}

	/**
	 * 通知権限をリクエスト
	 */
	async requestNotificationPermission() {
		if (typeof window === 'undefined') {
			return false;
		}
		
		if ('Notification' in window && Notification.permission === 'default') {
			const permission = await Notification.requestPermission();
			console.log('TimerService: 通知権限:', permission);
			return permission === 'granted';
		}
		return Notification.permission === 'granted';
	}

	/**
	 * サービスを破棄
	 */
	destroy() {
		console.log('TimerService: サービスを破棄');
		
		this.stopTimer();
		this.stopPomodoroTimer();
		this.isInitialized = false;
	}
}

// シングルトンインスタンスを作成
export const timerService = new TimerService();