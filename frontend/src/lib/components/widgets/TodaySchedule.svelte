<script>
	import { onMount } from 'svelte';
	import { calendarData } from '$lib/stores/newsStore.js';
	import { api } from '$lib/utils/api.js';
	import { formatTime } from '$lib/utils/dateTime.js';

	let todayCache = null;
	let lastCacheTime = 0;

	onMount(async () => {
		await loadCalendarEvents();
	});

	async function loadCalendarEvents() {
		const today = new Date().toDateString();
		
		// キャッシュをチェック（1分間有効）
		if (todayCache && today === todayCache.date && Date.now() - lastCacheTime < 60000) {
			// 祝日データをデバッグ
			const holidays = todayCache.events.filter(event => event.source === 'japanese_holidays');
			if (holidays.length > 0) {
				console.log('キャッシュから今日の予定に祝日データが見つかりました:', holidays);
			}
			calendarData.set({
				events: todayCache.events,
				loading: false,
				error: null
			});
			return;
		}

		try {
			console.log('今日の予定を読み込み中...');
			const data = await api.getTodayEvents();
			if (data.success) {
				const events = data.data.events;
				console.log(`今日の予定数: ${events.length}`);
				
				// 祝日データをデバッグ
				const holidays = events.filter(event => event.source === 'japanese_holidays');
				if (holidays.length > 0) {
					console.log('APIから今日の予定に祝日データが見つかりました:', holidays);
				}
				
				calendarData.set({
					events: events,
					loading: false,
					error: null
				});
				
				// キャッシュに保存
				todayCache = {
					date: today,
					events: events
				};
				lastCacheTime = Date.now();
			} else {
				console.error('今日の予定APIからのレスポンスが失敗:', data);
			}
		} catch (error) {
			console.error('今日の予定の読み込みエラー:', error);
			calendarData.update(state => ({
				...state,
				loading: false,
				error: error.message
			}));
		}
	}

	async function refreshSchedule() {
		// キャッシュをクリア
		todayCache = null;
		lastCacheTime = 0;
		// データを再読み込み
		await loadCalendarEvents();
	}
</script>

<div class="widget today-schedule">
	<div class="schedule-header mb-3 flex justify-between items-center">
		<h3 class="text-sm text-secondary">今日の予定</h3>
		<button 
			class="btn btn-xs btn-secondary" 
			on:click={refreshSchedule}
			disabled={$calendarData.loading}
		>
			<i class="fas fa-sync-alt {$calendarData.loading ? 'animate-spin' : ''}"></i>
		</button>
	</div>
	
	{#if $calendarData.loading}
		<div class="text-center text-muted text-sm py-4">
			<i class="fas fa-spinner fa-spin"></i>
			読み込み中...
		</div>
	{:else if $calendarData.error}
		<div class="text-center text-danger text-sm py-4">
			<i class="fas fa-exclamation-triangle"></i>
			エラー
		</div>
	{:else if $calendarData.events.length === 0}
		<div class="text-center text-muted text-sm py-4">
			<i class="fas fa-calendar-check"></i>
			予定なし
		</div>
	{:else}
		<div class="schedule-list">
			{#each $calendarData.events.sort((a, b) => {
				// 祝日を優先的に表示
				if (a.source === 'japanese_holidays' && b.source !== 'japanese_holidays') return -1;
				if (b.source === 'japanese_holidays' && a.source !== 'japanese_holidays') return 1;
				return 0;
			}).slice(0, 5) as event}
				<div class="schedule-item mb-2 {event.source === 'japanese_holidays' ? 'holiday-event' : ''}" style="border-left: 3px solid {event.color || '#3b82f6'};">
					<div class="event-time text-xs text-secondary mb-1">
						{formatTime(event.start)}
						{#if event.source === 'japanese_holidays'}
							<span class="ml-1">🇯🇵</span>
						{/if}
					</div>
					<div class="event-title text-sm text-primary font-medium">
						{event.title}
					</div>
					{#if event.location}
						<div class="event-location text-xs text-muted">
							<i class="fas fa-map-marker-alt mr-1"></i>
							{event.location}
						</div>
					{/if}
				</div>
			{/each}
			
			{#if $calendarData.events.length > 5}
				<div class="more-events text-xs text-secondary text-center mt-2">
					+{$calendarData.events.length - 5}件の予定
				</div>
			{/if}
		</div>
	{/if}
</div>
