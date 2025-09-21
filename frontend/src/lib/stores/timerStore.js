import { writable } from 'svelte/store';

// 通常タイマーの状態
export const timer = writable({
	seconds: 0,           // 残り秒数
	isRunning: false,     // 実行中かどうか
	isPaused: false,      // 一時停止中かどうか
	totalSeconds: 0,      // 設定された総秒数
	startTime: null,      // 開始時刻
	pauseTime: null       // 一時停止時刻
});

// ポモドーロタイマーの状態
export const pomodoroTimer = writable({
	seconds: 0,           // 残り秒数
	isRunning: false,     // 実行中かどうか
	isPaused: false,      // 一時停止中かどうか
	phase: 'work',        // 現在のフェーズ: 'work', 'break', 'longBreak'
	sessions: 0,          // 完了したセッション数
	totalSessions: 4,     // 総セッション数
	workDuration: 25 * 60,    // 作業時間（秒）
	breakDuration: 5 * 60,    // 休憩時間（秒）
	longBreakDuration: 15 * 60, // 長い休憩時間（秒）
	totalSeconds: 0,      // 現在のフェーズの総秒数
	startTime: null,      // 開始時刻
	pauseTime: null       // 一時停止時刻
});

// タイマー設定の状態
export const timerSettings = writable({
	workTime: 25,         // 作業時間（分）
	breakTime: 5,         // 休憩時間（分）
	longBreakTime: 15,    // 長い休憩時間（分）
	sessions: 4           // セッション数
});

// カスタムタイマー設定の状態
export const customTimerSettings = writable([]);