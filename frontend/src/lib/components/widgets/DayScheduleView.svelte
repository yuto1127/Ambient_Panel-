<script>
	import { formatTime, formatDateTime } from '$lib/utils/dateTime.js';

	export let events = [];
	export let selectedDate = new Date();
	export let onBackToMonth = () => {};

	// 24時間の時間軸を生成
	const timeSlots = Array.from({ length: 24 }, (_, i) => i);

	// イベントを時間順にソート
	$: sortedEvents = events.sort((a, b) => {
		const timeA = new Date(a.start).getHours() * 60 + new Date(a.start).getMinutes();
		const timeB = new Date(b.start).getHours() * 60 + new Date(b.start).getMinutes();
		return timeA - timeB;
	});

	// 終日イベントと通常イベントを分離
	$: allDayEvents = events.filter(event => {
		// 終日イベントの判定：複数の条件をチェック
		const isAllDay = event.all_day || 
			// 明示的にall_dayフラグが設定されている
			(event.start && event.end && 
			 event.start.split('T')[0] === event.end.split('T')[0] && 
			 event.start.includes('T00:00:00')) ||
			// 開始時間が00:00:00の場合
			(event.start && event.end && 
			 event.start.split('T')[0] === event.end.split('T')[0] && 
			 event.start.includes('T00:00:00+09:00')) ||
			// 日本時間で00:00:00の場合
			(event.source === 'japanese_holidays') || // 祝日は終日として扱う
			// 祝日データソースの場合
			(event.title && event.title.includes('の日')) || // 「○○の日」形式の祝日
			(event.title && event.title.includes('祝日')) || // 「○○祝日」形式
			(event.title && event.title.includes('祭')) || // 「○○祭」形式
			(event.title && event.title.includes('節')) || // 「○○節」形式
			(event.title && event.title.includes('記念日')) || // 「○○記念日」形式
			// 日付のみの形式（時間情報がない）
			(event.start && !event.start.includes('T')) ||
			// 24時間のイベント（開始と終了が同じ日で、開始が00:00、終了が23:59または翌日00:00）
			(event.start && event.end && 
			 event.start.split('T')[0] === event.end.split('T')[0] && 
			 (event.start.includes('T00:00') && event.end.includes('T23:59'))) ||
			(event.start && event.end && 
			 event.start.split('T')[0] !== event.end.split('T')[0] && 
			 event.start.includes('T00:00') && event.end.includes('T00:00'));
		
		return isAllDay;
	});
	$: regularEvents = events.filter(event => {
		const isAllDay = event.all_day || 
			(event.start && event.end && 
			 event.start.split('T')[0] === event.end.split('T')[0] && 
			 event.start.includes('T00:00:00')) ||
			(event.start && event.end && 
			 event.start.split('T')[0] === event.end.split('T')[0] && 
			 event.start.includes('T00:00:00+09:00')) ||
			(event.source === 'japanese_holidays') ||
			(event.title && event.title.includes('の日')) ||
			(event.title && event.title.includes('祝日')) ||
			(event.title && event.title.includes('祭')) ||
			(event.title && event.title.includes('節')) ||
			(event.title && event.title.includes('記念日')) ||
			(event.start && !event.start.includes('T')) ||
			(event.start && event.end && 
			 event.start.split('T')[0] === event.end.split('T')[0] && 
			 (event.start.includes('T00:00') && event.end.includes('T23:59'))) ||
			(event.start && event.end && 
			 event.start.split('T')[0] !== event.end.split('T')[0] && 
			 event.start.includes('T00:00') && event.end.includes('T00:00'));
		return !isAllDay;
	});

	// デバッグ用：イベントデータをログ出力
	$: if (events.length > 0) {
		console.log('DayScheduleView: 全イベント', events.map(e => ({ 
			title: e.title, 
			source: e.source, 
			start: e.start, 
			end: e.end,
			all_day: e.all_day,
			location: e.location,
			description: e.description
		})));
		console.log('DayScheduleView: 終日イベント', allDayEvents.map(e => ({ 
			title: e.title, 
			source: e.source,
			all_day: e.all_day,
			start: e.start,
			end: e.end
		})));
		console.log('DayScheduleView: 通常イベント', regularEvents.map(e => ({ 
			title: e.title, 
			source: e.source,
			all_day: e.all_day,
			start: e.start,
			end: e.end
		})));
		
		// 祝日データの詳細確認
		const holidays = events.filter(e => e.source === 'japanese_holidays');
		console.log('DayScheduleView: 祝日データ', holidays);
		
		// 終日判定の詳細デバッグ
		events.forEach(event => {
			const isAllDay = event.all_day || 
				(event.start && event.end && 
				 event.start.split('T')[0] === event.end.split('T')[0] && 
				 event.start.includes('T00:00:00')) ||
				(event.start && event.end && 
				 event.start.split('T')[0] === event.end.split('T')[0] && 
				 event.start.includes('T00:00:00+09:00')) ||
				(event.source === 'japanese_holidays') ||
				(event.title && event.title.includes('の日')) ||
				(event.title && event.title.includes('祝日')) ||
				(event.title && event.title.includes('祭')) ||
				(event.title && event.title.includes('節')) ||
				(event.title && event.title.includes('記念日')) ||
				(event.start && !event.start.includes('T')) ||
				(event.start && event.end && 
				 event.start.split('T')[0] === event.end.split('T')[0] && 
				 (event.start.includes('T00:00') && event.end.includes('T23:59'))) ||
				(event.start && event.end && 
				 event.start.split('T')[0] !== event.end.split('T')[0] && 
				 event.start.includes('T00:00') && event.end.includes('T00:00'));
			
			console.log(`DayScheduleView: イベント "${event.title}" の終日判定:`, {
				all_day: event.all_day,
				start: event.start,
				end: event.end,
				source: event.source,
				isAllDay: isAllDay,
				hasTimeInfo: event.start && event.start.includes('T'),
				isSameDay: event.start && event.end && event.start.split('T')[0] === event.end.split('T')[0]
			});
		});
	}

	// 指定された時間のイベントを取得
	function getEventsAtHour(hour) {
		return sortedEvents.filter(event => {
			const eventStart = new Date(event.start);
			const eventEnd = new Date(event.end);
			const eventStartHour = eventStart.getHours();
			const eventEndHour = eventEnd.getHours();
			
			// 終日イベントの場合は0時から23時まで表示
			if (event.all_day) {
				return hour >= 0 && hour <= 23;
			}
			
			// イベントがこの時間帯に含まれるかチェック
			// イベントの開始時間がこの時間帯内にあるか、またはこの時間帯がイベントの時間範囲内にあるか
			return (eventStartHour <= hour && eventEndHour > hour) || 
				   (eventStartHour === hour);
		});
	}

	// 時間の表示形式
	function formatHour(hour) {
		return `${hour.toString().padStart(2, '0')}:00`;
	}

	// イベントの高さを計算（分単位）
	function getEventHeight(event) {
		const start = new Date(event.start);
		const end = new Date(event.end);
		const durationMinutes = (end - start) / (1000 * 60);
		
		// 最小40分、最大6時間（より多くの情報を表示するため高さを増加）
		const minHeight = 40;
		const maxHeight = 360;
		return Math.max(minHeight, Math.min(maxHeight, durationMinutes));
	}

	// イベントの開始位置を計算（分単位）
	function getEventTop(event) {
		const start = new Date(event.start);
		return start.getHours() * 60 + start.getMinutes();
	}

	// イベントの幅を計算（重複するイベントがある場合）
	function getEventWidth(event, index, totalEvents) {
		// 同じ時間帯のイベント数を計算
		const eventStart = new Date(event.start);
		const eventEnd = new Date(event.end);
		const overlappingEvents = sortedEvents.filter(otherEvent => {
			if (otherEvent === event) return false;
			const otherStart = new Date(otherEvent.start);
			const otherEnd = new Date(otherEvent.end);
			
			// 時間が重複しているかチェック
			return (eventStart < otherEnd && eventEnd > otherStart);
		});
		
		const overlappingCount = overlappingEvents.length + 1; // +1 for current event
		return 100 / overlappingCount;
	}

	// イベントの左位置を計算
	function getEventLeft(event, index, totalEvents) {
		// 同じ時間帯のイベント数を計算
		const eventStart = new Date(event.start);
		const eventEnd = new Date(event.end);
		const overlappingEvents = sortedEvents.filter(otherEvent => {
			if (otherEvent === event) return false;
			const otherStart = new Date(otherEvent.start);
			const otherEnd = new Date(otherEvent.end);
			
			// 時間が重複しているかチェック
			return (eventStart < otherEnd && eventEnd > otherStart);
		});
		
		const overlappingCount = overlappingEvents.length + 1; // +1 for current event
		const positionInOverlap = sortedEvents.slice(0, index).filter(otherEvent => {
			if (otherEvent === event) return false;
			const otherStart = new Date(otherEvent.start);
			const otherEnd = new Date(otherEvent.end);
			
			// 時間が重複しているかチェック
			return (eventStart < otherEnd && eventEnd > otherStart);
		}).length;
		
		return (100 / overlappingCount) * positionInOverlap;
	}
</script>

<div class="day-schedule-view">
	<div class="schedule-header">
		<div class="schedule-header-left">
			<button class="btn btn-sm btn-secondary" on:click={onBackToMonth}>
				<i class="fas fa-arrow-left"></i>
				月表示に戻る
			</button>
		</div>
		<div class="schedule-header-center">
			<h3 class="schedule-title">
				{formatDateTime(selectedDate).date} の予定
			</h3>
		</div>
		<div class="schedule-header-right">
			<div class="schedule-summary">
				{#if events.length === 0}
					<span class="text-muted">予定はありません</span>
				{:else}
					<span class="text-primary">{events.length}件の予定</span>
				{/if}
			</div>
		</div>
	</div>

	<!-- 統合されたスケジュール表示 -->
	<div class="unified-schedule-container">
		<!-- 終日予定セクション -->
		{#if allDayEvents.length > 0}
			<div class="allday-section">
				<div class="allday-header">
					<div class="allday-label">終日</div>
				</div>
				<div class="allday-events">
					{#each allDayEvents as event, index}
						<div 
							class="allday-event"
							class:holiday-event={event.source === 'japanese_holidays' || event.title.includes('の日') || event.title.includes('祝日') || event.title.includes('祭') || event.title.includes('節') || event.title.includes('記念日')}
						>
							<div class="event-content">
								<div class="event-title">{event.title}</div>
								<div class="event-time">終日</div>
								{#if event.source === 'japanese_holidays'}
									<div class="event-source">🇯🇵 祝日</div>
								{:else if event.source === 'icloud'}
									<div class="event-source">📱 iCloud</div>
								{:else}
									<div class="event-source">📅 カレンダー</div>
								{/if}
								{#if event.location}
									<div class="event-location">
										<i class="fas fa-map-marker-alt"></i>
										{event.location}
									</div>
								{/if}
								{#if event.description}
									<div class="event-description">
										{event.description}
									</div>
								{/if}
							</div>
						</div>
					{/each}
				</div>
			</div>
		{:else}
			<!-- 終日イベントがない場合 -->
			<div class="allday-section">
				<div class="allday-header">
					<div class="allday-label">終日</div>
				</div>
				<div class="allday-events">
					<div class="no-events">
						<span class="text-muted">終日予定はありません</span>
					</div>
				</div>
			</div>
		{/if}

		<!-- 24時間タイムライン -->
		<div class="schedule-timeline">
			<div class="time-column">
				{#each timeSlots as hour}
					<div class="time-slot" style="height: 60px;">
						<div class="time-label">
							{formatHour(hour)}
						</div>
					</div>
				{/each}
			</div>

			<div class="events-column">
				{#each timeSlots as hour}
					<div class="hour-slot" style="height: 60px;"></div>
				{/each}
				
				<!-- 通常のイベントを直接配置 -->
				{#each regularEvents as event, index}
					<div 
						class="event-block"
						style="
							background-color: {event.color || '#3b82f6'};
							height: {getEventHeight(event)}px;
							top: {getEventTop(event)}px;
							width: {getEventWidth(event, index, regularEvents.length)}%;
							left: {getEventLeft(event, index, regularEvents.length)}%;
							z-index: {10 + index};
						"
					>
						<div class="event-content">
							<div class="event-title">{event.title}</div>
							<div class="event-time">
								{formatTime(event.start)} - {formatTime(event.end)}
							</div>
							{#if event.location}
								<div class="event-location">
									<i class="fas fa-map-marker-alt"></i>
									{event.location}
								</div>
							{/if}
							{#if event.description}
								<div class="event-description">
									{event.description}
								</div>
							{/if}
							{#if event.source}
								<div class="event-source">
									{event.source === 'icloud' ? '📱 iCloud' : event.source === 'japanese_holidays' ? '🇯🇵 祝日' : '📅 カレンダー'}
								</div>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		</div>
	</div>
</div>

<style>
	.day-schedule-view {
		background: var(--card-bg);
		border-radius: 12px;
		padding: 20px;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
		min-height: 400px;
		max-height: calc(100vh - 150px);
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.unified-schedule-container {
		flex: 1;
		display: flex;
		flex-direction: column;
		overflow-y: auto;
		border: 1px solid var(--border-color);
		border-radius: 8px;
		background: var(--bg-primary);
		min-height: 0;
	}

	/* 統合コンテナのスクロールバー */
	.unified-schedule-container::-webkit-scrollbar {
		width: 8px;
	}

	.unified-schedule-container::-webkit-scrollbar-track {
		background: var(--bg-tertiary);
		border-radius: 4px;
	}

	.unified-schedule-container::-webkit-scrollbar-thumb {
		background: var(--border-color);
		border-radius: 4px;
	}

	.unified-schedule-container::-webkit-scrollbar-thumb:hover {
		background: var(--text-muted);
	}

	.schedule-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20px;
		padding-bottom: 15px;
		border-bottom: 2px solid var(--border-color);
		gap: 20px;
	}

	.schedule-header-left {
		flex-shrink: 0;
	}

	.schedule-header-center {
		flex: 1;
		text-align: center;
	}

	.schedule-header-right {
		flex-shrink: 0;
	}

	.schedule-title {
		font-size: 1.5rem;
		font-weight: 600;
		color: var(--text-primary);
		margin: 0;
	}

	.schedule-summary {
		font-size: 0.9rem;
		color: var(--text-secondary);
	}

	.allday-section {
		margin: 0;
		border: none;
		border-bottom: 1px solid var(--border-color);
		border-radius: 0;
		background: transparent;
		overflow: visible;
		min-height: auto;
		max-height: none;
		flex-shrink: 0;
	}

	.allday-header {
		background: var(--bg-secondary);
		padding: 8px 12px;
		border-bottom: 1px solid var(--border-color);
	}

	.allday-label {
		font-size: 0.8rem;
		font-weight: 600;
		color: var(--text-secondary);
	}

	.allday-events {
		padding: 8px;
		display: flex;
		flex-direction: column;
		gap: 6px;
		min-height: auto;
		max-height: none;
		overflow: visible;
	}

	.allday-event {
		background: linear-gradient(135deg, #87ceeb, #b0e0e6) !important;
		color: #1e3a8a !important;
		font-weight: bold !important;
		border-radius: 6px !important;
		padding: 10px 12px !important;
		margin: 2px 0 !important;
		text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5) !important;
		box-shadow: 0 2px 4px rgba(135, 206, 235, 0.3) !important;
		border: 1px solid rgba(30, 58, 138, 0.2) !important;
		cursor: pointer;
		transition: all 0.2s ease;
		min-height: auto;
		height: auto;
		overflow: visible;
		word-wrap: break-word;
		overflow-wrap: break-word;
		white-space: normal;
	}

	.allday-event:hover {
		transform: translateY(-1px);
		box-shadow: 0 4px 8px rgba(135, 206, 235, 0.4) !important;
	}

	.allday-event .event-title {
		color: #1e3a8a !important;
		font-weight: bold !important;
		text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5) !important;
		font-size: 0.95rem;
		line-height: 1.3;
		word-wrap: break-word;
		overflow-wrap: break-word;
		white-space: normal;
		max-width: 100%;
		margin-bottom: 4px;
	}

	.allday-event .event-time {
		color: rgba(30, 58, 138, 0.8) !important;
		font-weight: 500 !important;
		font-size: 0.8rem;
	}

	.allday-event .event-location {
		color: rgba(30, 58, 138, 0.7) !important;
		font-size: 0.8rem;
		word-wrap: break-word;
		overflow-wrap: break-word;
		white-space: normal;
		max-width: 100%;
		margin-top: 2px;
	}

	.allday-event .event-description {
		color: rgba(30, 58, 138, 0.8) !important;
		font-size: 0.8rem;
		margin-top: 4px;
		line-height: 1.2;
		word-wrap: break-word;
		overflow-wrap: break-word;
		white-space: normal;
		max-width: 100%;
	}

	.allday-event .event-source {
		color: rgba(30, 58, 138, 0.9) !important;
		font-size: 0.75rem;
		font-weight: 600;
		margin-top: 3px;
	}

	.allday-event.holiday-event {
		background: linear-gradient(135deg, #87ceeb, #b0e0e6) !important;
		border: 2px solid rgba(30, 58, 138, 0.3) !important;
		box-shadow: 0 3px 6px rgba(135, 206, 235, 0.4) !important;
	}

	.allday-event.holiday-event:hover {
		box-shadow: 0 5px 10px rgba(135, 206, 235, 0.5) !important;
		transform: translateY(-2px);
	}

	.no-events {
		padding: 12px;
		text-align: center;
		font-size: 0.9rem;
		color: var(--text-muted);
		font-style: italic;
	}

	.schedule-timeline {
		display: flex;
		flex: 1;
		min-height: 300px;
		overflow: visible;
		border: none;
		border-radius: 0;
		background: transparent;
	}

	.time-column {
		width: 80px;
		background: var(--bg-secondary);
		border-right: 1px solid var(--border-color);
		flex-shrink: 0;
	}

	.time-slot {
		display: flex;
		align-items: center;
		justify-content: center;
		border-bottom: 1px solid var(--border-color);
		position: relative;
		height: 60px;
		min-height: 60px;
	}

	.time-label {
		font-size: 0.8rem;
		color: var(--text-secondary);
		font-weight: 500;
	}

	.events-column {
		flex: 1;
		position: relative;
		background: var(--bg-primary);
	}

	.hour-slot {
		border-bottom: 1px solid var(--border-color);
		position: relative;
		height: 60px;
		min-height: 60px;
	}

	.event-block {
		position: absolute;
		border-radius: 6px;
		padding: 10px;
		margin: 2px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
		cursor: pointer;
		transition: all 0.2s ease;
		border-left: 4px solid rgba(255, 255, 255, 0.3);
		min-height: 50px;
		overflow: hidden;
	}

	.event-block:hover {
		transform: translateY(-1px);
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
	}


	.event-content {
		display: flex;
		flex-direction: column;
		gap: 3px;
		height: 100%;
		overflow: hidden;
	}

	.event-title {
		font-weight: 600;
		font-size: 0.95rem;
		line-height: 1.3;
		color: white;
		text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
		word-wrap: break-word;
		overflow-wrap: break-word;
		white-space: normal;
		max-width: 100%;
	}

	.event-time {
		font-size: 0.8rem;
		opacity: 0.9;
		color: white;
		font-weight: 500;
	}

	.event-location {
		font-size: 0.75rem;
		opacity: 0.8;
		color: white;
		display: flex;
		align-items: center;
		gap: 4px;
		word-wrap: break-word;
		overflow-wrap: break-word;
		white-space: normal;
		max-width: 100%;
	}

	.event-location i {
		font-size: 0.65rem;
		flex-shrink: 0;
	}

	.event-description {
		font-size: 0.7rem;
		opacity: 0.85;
		color: white;
		word-wrap: break-word;
		overflow-wrap: break-word;
		white-space: normal;
		max-width: 100%;
		line-height: 1.2;
		margin-top: 2px;
	}

	.event-source {
		font-size: 0.65rem;
		opacity: 0.7;
		color: white;
		font-weight: 500;
		margin-top: 2px;
	}

	/* ダークモード対応 */
	:global(.dark) .day-schedule-view {
		background: var(--card-bg-dark);
	}

	:global(.dark) .schedule-timeline {
		background: var(--bg-primary-dark);
		border-color: var(--border-color-dark);
	}

	:global(.dark) .time-column {
		background: var(--bg-secondary-dark);
		border-color: var(--border-color-dark);
	}

	:global(.dark) .events-column {
		background: var(--bg-primary-dark);
	}

	:global(.dark) .hour-slot {
		border-color: var(--border-color-dark);
	}

	:global(.dark) .time-slot {
		border-color: var(--border-color-dark);
	}

	:global(.dark) .schedule-header {
		border-color: var(--border-color-dark);
	}

	:global(.dark) .allday-section {
		background: var(--bg-primary-dark);
		border-color: var(--border-color-dark);
	}

	:global(.dark) .allday-header {
		background: var(--bg-secondary-dark);
		border-color: var(--border-color-dark);
	}

	/* レスポンシブ対応 */
	@media (max-width: 768px) {
		.day-schedule-view {
			max-height: calc(100vh - 100px);
			padding: 15px;
		}

		.unified-schedule-container {
			min-height: 200px;
		}

		.schedule-timeline {
			min-height: 200px;
		}

		.time-column {
			width: 60px;
		}

		.time-label {
			font-size: 0.7rem;
		}

		.event-title {
			font-size: 0.8rem;
		}

		.event-time {
			font-size: 0.7rem;
		}

		.event-location {
			font-size: 0.65rem;
		}

		.allday-event {
			padding: 8px 10px !important;
		}

		.allday-event .event-title {
			font-size: 0.9rem;
		}

		.allday-event .event-location {
			font-size: 0.75rem;
		}

		.allday-event .event-description {
			font-size: 0.75rem;
		}

		/* モバイル用スクロールバー */
		.unified-schedule-container::-webkit-scrollbar {
			width: 6px;
		}
	}
</style>
