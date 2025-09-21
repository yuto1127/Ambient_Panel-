<script>
	import { onMount, tick } from 'svelte';
	import { calendarView, calendarEvents, selectedDayEvents, CalendarUtils } from '$lib/stores/calendarStore.js';
	import { api } from '$lib/utils/api.js';
	import { formatTime, formatDateTime } from '$lib/utils/dateTime.js';
	import DayScheduleView from '$lib/components/widgets/DayScheduleView.svelte';

	let loading = false;
	let error = null;
	let cache = new Map(); // フロントエンドキャッシュ
	let forceRender = 0; // 強制再レンダリング用のカウンター

	console.log('CalendarTab: コンポーネントがマウントされました');

	onMount(async () => {
		// カレンダービューの初期化を確実にする
		const now = new Date();
		calendarView.update(view => ({
			...view,
			currentDate: now,
			selectedDate: now
		}));
		
		// 初期月を設定
		lastLoadedMonth = `${now.getFullYear()}-${now.getMonth() + 1}`;
		
		await loadCalendarEvents();
		isInitialized = true;
		
		// 定期的にカレンダーをチェック（5分間隔）
		const interval = setInterval(() => {
			if (isInitialized) {
				console.log('定期的なカレンダーチェックを実行中...');
				loadCalendarEvents();
			}
		}, 300000); // 5分間隔
		
		// クリーンアップ
		return () => {
			clearInterval(interval);
		};
	});

	// calendarViewの変更を監視してイベントを再読み込み（初期化後のみ）
	let isInitialized = false;
	let lastLoadedMonth = null;
	
	$: if ($calendarView.currentDate && isInitialized) {
		const currentMonth = `${$calendarView.currentDate.getFullYear()}-${$calendarView.currentDate.getMonth() + 1}`;
		if (lastLoadedMonth !== currentMonth) {
			console.log(`月が変更されました: ${lastLoadedMonth} -> ${currentMonth}`);
			lastLoadedMonth = currentMonth;
			loadCalendarEvents();
		}
	}

	// calendarEventsの変更を監視して強制再レンダリングをトリガー
	let lastEventCount = -1;
	$: if ($calendarEvents !== undefined) {
		const currentEventCount = $calendarEvents.length;
		if (currentEventCount !== lastEventCount) {
			console.log(`カレンダーイベントが更新されました: ${currentEventCount}件 (前回: ${lastEventCount}件)`);
			lastEventCount = currentEventCount;
			forceRender = forceRender + 1; // 強制再レンダリングをトリガー
			console.log(`forceRenderカウンター: ${forceRender}`);
		}
	}

	// forceRenderの変更を監視してデバッグ情報を出力
	$: if (forceRender > 0) {
		console.log(`カレンダーグリッドが再レンダリングされます (forceRender: ${forceRender})`);
	}

	async function loadCalendarEvents() {
		const currentDate = $calendarView.currentDate;
		if (!currentDate || isNaN(currentDate.getTime())) {
			console.error('Invalid currentDate:', currentDate);
			return;
		}

		const cacheKey = `${currentDate.getFullYear()}-${currentDate.getMonth() + 1}`;

		// キャッシュをチェック
		if (cache.has(cacheKey)) {
			const cachedData = cache.get(cacheKey);
			if (Date.now() - cachedData.timestamp < 60000) { // 1分間キャッシュ（短縮）
				console.log(`キャッシュからイベントを読み込み: ${cacheKey}`);
				// 祝日データをデバッグ
				const holidays = cachedData.events.filter(event => event.source === 'japanese_holidays');
				console.log(`キャッシュから祝日データ: ${holidays.length}件`, holidays);
				// ストアを確実に更新
				calendarEvents.set([...cachedData.events]); // 新しい配列を作成して確実に変更を検知
				// DOMの更新を待ってから強制再レンダリングをトリガー
				await tick();
				forceRender = forceRender + 1;
				console.log('キャッシュからカレンダーの表示を更新しました');
				
				// 複数回の強制更新を確実に実行
				setTimeout(() => {
					forceRender = forceRender + 1;
					console.log('キャッシュからの1回目の追加強制更新を実行しました');
				}, 50);
				
				setTimeout(() => {
					forceRender = forceRender + 1;
					console.log('キャッシュからの2回目の追加強制更新を実行しました');
				}, 150);
				return;
			}
		}

		// 既に読み込み中の場合は重複を避ける
		if (loading) {
			console.log('既に読み込み中です');
			return;
		}

		loading = true;
		error = null;
		
		try {
			console.log(`カレンダーイベントを読み込み中: ${currentDate.getFullYear()}年${currentDate.getMonth() + 1}月`);
			
			// 現在の月のイベントを取得
			const data = await api.getMonthEvents(currentDate.getFullYear(), currentDate.getMonth() + 1);
			
			if (data.success) {
				const events = data.data.events || [];
				console.log(`読み込まれたイベント数: ${events.length}`);
				
				// 祝日データをデバッグ
				const holidays = events.filter(event => event.source === 'japanese_holidays');
				console.log(`APIから祝日データ: ${holidays.length}件`, holidays);
				
				// 祝日の詳細をログ出力
				holidays.forEach(holiday => {
					console.log(`祝日詳細: ${holiday.title} (${holiday.start}) - source: ${holiday.source}`);
				});

				// ストアを確実に更新
				calendarEvents.set([...events]); // 新しい配列を作成して確実に変更を検知

				// キャッシュに保存
				cache.set(cacheKey, {
					events: events,
					timestamp: Date.now()
				});

				// DOMの更新を待ってから強制再レンダリングをトリガー
				await tick();
				forceRender = forceRender + 1;
				console.log('カレンダーの表示を更新しました');
				
				// 複数回の強制更新を確実に実行
				setTimeout(() => {
					forceRender = forceRender + 1;
					console.log('1回目の追加強制更新を実行しました');
				}, 50);
				
				setTimeout(() => {
					forceRender = forceRender + 1;
					console.log('2回目の追加強制更新を実行しました');
				}, 150);
				
				setTimeout(() => {
					forceRender = forceRender + 1;
					console.log('3回目の追加強制更新を実行しました');
				}, 300);
			} else {
				console.error('カレンダーAPIからのレスポンスが失敗:', data);
			}
		} catch (err) {
			error = err.message;
			console.error('カレンダーイベントの読み込みエラー:', err);
		} finally {
			loading = false;
		}
	}

	async function selectDate(date) {
		if (!date || isNaN(date.getTime())) {
			console.error('Invalid date passed to selectDate:', date);
			return;
		}
		
		calendarView.update(state => ({
			...state,
			selectedDate: date,
			view: 'day'
		}));
		
		// 選択された日のイベントを取得
		const dayEvents = getDayEvents(date);
		selectedDayEvents.set(dayEvents);
	}

	function navigateMonth(direction) {
		const currentDate = $calendarView.currentDate;
		if (!currentDate || isNaN(currentDate.getTime())) {
			console.error('Invalid currentDate for navigation:', currentDate);
			return;
		}
		
		console.log(`ナビゲーション開始: direction=${direction}, 現在の月=${currentDate.getFullYear()}年${currentDate.getMonth() + 1}月`);
		
		// CalendarUtilsを使用して月を移動
		const directionStr = direction === -1 ? 'prev' : 'next';
		console.log(`方向文字列: ${directionStr}`);
		
		const newDate = CalendarUtils.navigateMonth(currentDate, directionStr);
		
		if (isNaN(newDate.getTime())) {
			console.error('Invalid newDate after navigation:', newDate);
			return;
		}
		
		console.log(`ナビゲーション完了: ${currentDate.getFullYear()}年${currentDate.getMonth() + 1}月 → ${newDate.getFullYear()}年${newDate.getMonth() + 1}月`);
		
		const newMonthKey = `${newDate.getFullYear()}-${newDate.getMonth() + 1}`;
		
		calendarView.update(state => ({
			...state,
			currentDate: newDate
		}));
		
		// lastLoadedMonthを更新してリアクティブステートメントをトリガー
		lastLoadedMonth = newMonthKey;
		loadCalendarEvents();
	}

	function goToToday() {
		const today = CalendarUtils.goToToday();
		if (isNaN(today.getTime())) {
			console.error('Invalid today date:', today);
			return;
		}
		
		const todayMonth = `${today.getFullYear()}-${today.getMonth() + 1}`;
		
		calendarView.update(state => ({
			...state,
			currentDate: today,
			selectedDate: today,
			view: 'month'
		}));
		
		// lastLoadedMonthを更新してリアクティブステートメントをトリガー
		lastLoadedMonth = todayMonth;
		loadCalendarEvents();
	}

	function backToMonthView() {
		calendarView.update(state => ({
			...state,
			view: 'month'
		}));
	}

	async function refreshCalendar() {
		console.log('カレンダーを手動でリフレッシュ中...');
		// キャッシュをクリア
		cache.clear();
		// データを再読み込み
		await loadCalendarEvents();
		// 強制再レンダリングをトリガー
		forceRender = forceRender + 1;
		console.log('カレンダーのリフレッシュが完了しました');
		
		// 追加の強制更新
		setTimeout(() => {
			forceRender = forceRender + 1;
			console.log('リフレッシュ後の追加強制更新を実行しました');
		}, 100);
	}

	function getDayEvents(date) {
		// 日付の検証
		if (!date || isNaN(date.getTime())) {
			console.error('Invalid date passed to getDayEvents:', date);
			return [];
		}

		// 最新のイベントデータを確実に取得
		const events = $calendarEvents || [];
		if (!events || events.length === 0) {
			console.log('getDayEvents: イベントデータが空です');
			return [];
		}

		// 日本時間（JST）で日付文字列を取得
		const year = date.getFullYear();
		const month = String(date.getMonth() + 1).padStart(2, '0');
		const day = String(date.getDate()).padStart(2, '0');
		const dateStr = `${year}-${month}-${day}`;
		
		console.log(`getDayEvents: 日付 ${dateStr} のイベントを検索中...`);
		console.log(`getDayEvents: 全イベント数: ${events.length}`);
		
		const dayEvents = events.filter(event => {
			// イベントの開始日を取得
			let eventStartDate;
			
			if (event.start.includes('T')) {
				// 時間情報がある場合
				eventStartDate = event.start.split('T')[0];
			} else {
				// 時間情報がない場合（日付のみ）
				eventStartDate = event.start;
			}
			
			const matches = eventStartDate === dateStr;
			if (matches) {
				console.log(`マッチしたイベント: ${event.title} (${event.start}) - source: ${event.source}, all_day: ${event.all_day}`);
			}
			return matches;
		});

		// 終日イベントをデバッグ
		const allDayEvents = dayEvents.filter(event => {
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
			return isAllDay;
		});

		console.log(`getDayEvents: ${dateStr} の結果:`, {
			全日: dayEvents.length,
			終日イベント: allDayEvents.length,
			通常イベント: dayEvents.length - allDayEvents.length,
			終日イベント詳細: allDayEvents.map(e => ({ title: e.title, source: e.source, all_day: e.all_day }))
		});

		// 祝日データをデバッグ
		const holidays = dayEvents.filter(event => event.source === 'japanese_holidays');
		if (holidays.length > 0) {
			console.log(`祝日データが見つかりました: ${dateStr}`, holidays);
		} else if (dateStr === '2025-09-15' || dateStr === '2025-09-23') {
			console.log(`祝日データが見つかりません: ${dateStr}`, '全イベント:', events.filter(e => e.source === 'japanese_holidays'));
		}

		return dayEvents;
	}

	function getMonthName(date) {
		if (!date || isNaN(date.getTime())) {
			console.error('Invalid date passed to getMonthName:', date);
			return '無効な月';
		}
		const months = [
			'1月', '2月', '3月', '4月', '5月', '6月',
			'7月', '8月', '9月', '10月', '11月', '12月'
		];
		return months[date.getMonth()];
	}

	function getWeekDays() {
		return ['日', '月', '火', '水', '木', '金', '土'];
	}

	$: monthGrid = CalendarUtils.generateMonthGrid($calendarView.currentDate);
	$: selectedEvents = $selectedDayEvents;
	
	// カレンダーイベントの変更を監視して祝日表示を更新
	$: calendarEventsLength = $calendarEvents.length;
	$: calendarEventsData = $calendarEvents;
	$: if (calendarEventsLength > 0) {
		console.log(`カレンダーイベントが更新されました: ${calendarEventsLength}件`);
		// 祝日データの確認
		const holidays = calendarEventsData.filter(event => event.source === 'japanese_holidays');
		if (holidays.length > 0) {
			console.log(`祝日データ: ${holidays.length}件`, holidays.map(h => h.title));
		}
		// 強制再レンダリングをトリガー
		forceRender = forceRender + 1;
	}
</script>

<div class="tab-content active">
	<h2 class="text-primary mb-6">カレンダー</h2>
	
	{#if $calendarView.view === 'month'}
		<!-- 月表示 -->
		<div class="calendar-month-view">
			<!-- ヘッダー -->
			<div class="calendar-header">
				<div class="calendar-nav">
					<button class="btn btn-sm btn-secondary" on:click={() => navigateMonth(-1)}>
						<i class="fas fa-chevron-left"></i>
					</button>
					<h3 class="calendar-title">
						{$calendarView.currentDate.getFullYear()}年{getMonthName($calendarView.currentDate)}
					</h3>
					<button class="btn btn-sm btn-secondary" on:click={() => navigateMonth(1)}>
						<i class="fas fa-chevron-right"></i>
					</button>
				</div>
				<button class="btn btn-sm btn-primary" on:click={goToToday}>
					今日
				</button>
				<button class="btn btn-sm btn-secondary" on:click={refreshCalendar} disabled={loading} title="カレンダーを更新">
					<i class="fas fa-sync-alt {loading ? 'animate-spin' : ''}"></i>
					<span class="ml-1">更新</span>
				</button>
			</div>

			<!-- 曜日ヘッダー -->
			<div class="calendar-weekdays">
				{#each getWeekDays() as day}
					<div class="weekday">{day}</div>
				{/each}
			</div>

			<!-- カレンダーグリッド -->
			<div class="calendar-grid" key="{forceRender}-{$calendarEvents.length}-{$calendarView.currentDate.getTime()}-{Date.now()}">
				{#each monthGrid as date}
					{@const dayEvents = getDayEvents(date)}
					{@const holidayEvents = dayEvents.filter(event => event.source === 'japanese_holidays')}
					{@const regularEvents = dayEvents.filter(event => event.source !== 'japanese_holidays')}
					{@const isToday = CalendarUtils.isToday(date)}
					{@const isCurrentMonth = CalendarUtils.isCurrentMonth(date, $calendarView.currentDate)}
					{@const isSelected = CalendarUtils.isSelectedDate(date, $calendarView.selectedDate)}
					
					<button 
						class="calendar-day"
						class:today={isToday}
						class:other-month={!isCurrentMonth}
						class:selected={isSelected}
						class:has-events={dayEvents.length > 0}
						class:has-holiday={holidayEvents.length > 0}
						on:click={() => selectDate(date)}
						key="{date.getTime()}-{forceRender}-{$calendarEvents.length}-{dayEvents.length}-{Date.now()}"
					>
						<div class="day-header">
							<div class="day-number">{date.getDate()}</div>
							{#if holidayEvents.length > 0}
								<div class="holiday-indicator">
									<span class="holiday-text">{holidayEvents[0].title}</span>
								</div>
							{/if}
						</div>
						{#if regularEvents.length > 0}
							<div class="day-events">
								{#each regularEvents.slice(0, 2) as event}
									<div class="event-item">
										<div class="event-dot" style="background-color: {event.color || '#3b82f6'}"></div>
										<div class="event-title">{event.title.length > 12 ? event.title.substring(0, 12) + '...' : event.title}</div>
									</div>
								{/each}
								{#if regularEvents.length > 2}
									<div class="more-events">+{regularEvents.length - 2}</div>
								{/if}
							</div>
						{/if}
					</button>
				{/each}
			</div>
		</div>
	{:else}
		<!-- 日表示 -->
		<div class="calendar-day-view">
			{#if loading}
				<div class="flex flex-center" style="height: 200px;">
					<div class="text-center">
						<div class="text-2xl mb-4">
							<i class="fas fa-spinner fa-spin"></i>
						</div>
						<div class="text-lg">読み込み中...</div>
					</div>
				</div>
			{:else if error}
				<div class="text-center text-danger">
					<i class="fas fa-exclamation-triangle mb-2"></i>
					<div>エラー: {error}</div>
				</div>
			{:else}
				<!-- 24時間表示のスケジュールビュー -->
				<DayScheduleView 
					events={selectedEvents} 
					selectedDate={$calendarView.selectedDate}
					onBackToMonth={backToMonthView}
				/>
			{/if}
		</div>
	{/if}
</div>
