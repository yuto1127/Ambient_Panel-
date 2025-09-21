import { writable } from 'svelte/store';
import { isSameDay } from 'date-fns';

// カレンダー表示用のストア
export const calendarView = writable({
	currentDate: new Date(),
	selectedDate: new Date(),
	view: 'month' // 'month' or 'day'
});

// カレンダーイベントデータ
export const calendarEvents = writable([]);

// 選択された日のイベント
export const selectedDayEvents = writable([]);

// カレンダー表示のユーティリティ関数
export class CalendarUtils {
	// 月の最初の日を取得
	static getFirstDayOfMonth(date) {
		return new Date(date.getFullYear(), date.getMonth(), 1);
	}

	// 月の最後の日を取得
	static getLastDayOfMonth(date) {
		return new Date(date.getFullYear(), date.getMonth() + 1, 0);
	}

	// 月の最初の週の最初の日（日曜日）を取得
	static getFirstDayOfWeek(date) {
		const firstDay = this.getFirstDayOfMonth(date);
		const dayOfWeek = firstDay.getDay();
		return new Date(firstDay.getTime() - dayOfWeek * 24 * 60 * 60 * 1000);
	}

	// 月の最後の週の最後の日（土曜日）を取得
	static getLastDayOfWeek(date) {
		const lastDay = this.getLastDayOfMonth(date);
		const dayOfWeek = lastDay.getDay();
		const daysToAdd = 6 - dayOfWeek;
		return new Date(lastDay.getTime() + daysToAdd * 24 * 60 * 60 * 1000);
	}

	// 月のカレンダーグリッド用の日付配列を生成
	static generateMonthGrid(date) {
		const firstDay = this.getFirstDayOfWeek(date);
		const lastDay = this.getLastDayOfWeek(date);
		const days = [];
		
		const current = new Date(firstDay);
		while (current <= lastDay) {
			days.push(new Date(current));
			current.setDate(current.getDate() + 1);
		}
		
		return days;
	}

	// 日付が同じかチェック
	static isSameDate(date1, date2) {
		return date1.getFullYear() === date2.getFullYear() &&
			   date1.getMonth() === date2.getMonth() &&
			   date1.getDate() === date2.getDate();
	}

	// 日付が今日かチェック
	static isToday(date) {
		const today = new Date();
		return this.isSameDate(date, today);
	}

	// 日付が選択された日かチェック
	static isSelectedDate(date, selectedDate) {
		return this.isSameDate(date, selectedDate);
	}

	// 日付が現在の月かチェック
	static isCurrentMonth(date, currentMonth) {
		return date.getMonth() === currentMonth.getMonth() &&
			   date.getFullYear() === currentMonth.getFullYear();
	}

	// 日付をフォーマット（YYYY-MM-DD）
	static formatDateKey(date) {
		const year = date.getFullYear();
		const month = String(date.getMonth() + 1).padStart(2, '0');
		const day = String(date.getDate()).padStart(2, '0');
		return `${year}-${month}-${day}`;
	}

	// 指定された日のイベントを取得
	static getEventsForDate(events, date) {
		const dateKey = this.formatDateKey(date);
		return events.filter(event => {
			// イベントの開始時間を日本時間として解釈
			const eventDate = new Date(event.start + '+09:00');
			return this.formatDateKey(eventDate) === dateKey;
		});
	}

	// 月を移動
	static navigateMonth(currentDate, direction) {
		const year = currentDate.getFullYear();
		const month = currentDate.getMonth();
		const day = currentDate.getDate();
		
		let newYear = year;
		let newMonth = month;
		
		if (direction === 'prev') {
			newMonth = month - 1;
			if (newMonth < 0) {
				newYear--;
				newMonth = 11; // 12月
			}
		} else if (direction === 'next') {
			newMonth = month + 1;
			if (newMonth > 11) {
				newYear++;
				newMonth = 0; // 1月
			}
		}
		
		// 新しい日付を作成（日付が存在しない場合は月末に調整）
		const maxDay = new Date(newYear, newMonth + 1, 0).getDate();
		const adjustedDay = Math.min(day, maxDay);
		
		return new Date(newYear, newMonth, adjustedDay);
	}

	// 今日に戻る
	static goToToday() {
		return new Date();
	}

	// 特定の日のイベントを取得（詳細版）
	static getEventsForDateDetailed(allEvents, date) {
		return allEvents.filter(event => {
			const eventStart = new Date(event.start + '+09:00');
			const eventEnd = new Date(event.end + '+09:00');
			
			// 終日イベントの場合、日付のみで比較
			if (event.all_day) {
				// 終日イベントは開始日と終了日の間にあるすべての日を含む
				return date >= new Date(eventStart.getFullYear(), eventStart.getMonth(), eventStart.getDate()) &&
					   date < new Date(eventEnd.getFullYear(), eventEnd.getMonth(), eventEnd.getDate());
			} else {
				// 通常のイベントは開始日と終了日の間に含まれるか、開始日が同じ日
				return isSameDay(eventStart, date) || (eventStart < date && eventEnd > date);
			}
		}).sort((a, b) => new Date(a.start + '+09:00').getTime() - new Date(b.start + '+09:00').getTime());
	}
}
