import { format } from 'date-fns';
import { ja } from 'date-fns/locale';

export function formatDateTime(date) {
	const year = date.getFullYear();
	const month = date.getMonth() + 1;
	const day = date.getDate();
	const dayOfWeek = ['日', '月', '火', '水', '木', '金', '土'][date.getDay()];
	
	// 元号の計算
	let eraYear, eraName;
	if (year >= 2019) {
		// 令和
		eraYear = year - 2018;
		eraName = 'R';
	} else if (year >= 1989) {
		// 平成
		eraYear = year - 1988;
		eraName = 'H';
	} else if (year >= 1926) {
		// 昭和
		eraYear = year - 1925;
		eraName = 'S';
	} else {
		// 大正以前
		eraYear = year - 1911;
		eraName = 'T';
	}
	
	return {
		date: `${year}年(${eraName}${eraYear}) ${month}月${day}日(${dayOfWeek})`,
		time: format(date, 'HH:mm:ss', { locale: ja })
	};
}

export function formatTime(timeString) {
	// 入力値の検証
	if (!timeString || typeof timeString !== 'string') {
		console.error('formatTime: 無効な入力値:', timeString);
		return '--:--';
	}
	
	try {
		let date;
		
		// 日付のみの文字列（時刻情報なし）の場合は時刻を00:00に設定
		if (timeString.match(/^\d{4}-\d{2}-\d{2}$/)) {
			// 日付のみの場合は時刻を00:00に設定
			date = new Date(timeString + 'T00:00:00+09:00');
		} else if (timeString.includes('T')) {
			// ISO文字列の場合はそのまま使用
			date = new Date(timeString + '+09:00');
		} else {
			// その他の場合は時刻を00:00に設定
			date = new Date(timeString + 'T00:00:00+09:00');
		}
		
		// 日付の有効性をチェック
		if (isNaN(date.getTime())) {
			console.error('formatTime: 無効な日付:', timeString);
			return '--:--';
		}
		
		return format(date, 'HH:mm', { locale: ja });
	} catch (error) {
		console.error('formatTime: エラーが発生しました:', error, '入力値:', timeString);
		return '--:--';
	}
}

export function formatDuration(seconds) {
	const hours = Math.floor(seconds / 3600);
	const minutes = Math.floor((seconds % 3600) / 60);
	const secs = seconds % 60;
	
	if (hours > 0) {
		return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
	} else {
		return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
	}
}

export function updateDateTime() {
	const now = new Date();
	return formatDateTime(now);
}
