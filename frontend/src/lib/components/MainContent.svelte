<script>
	import TabNavigation from './TabNavigation.svelte';
	import SpotifyTab from './tabs/SpotifyTab.svelte';
	import CalendarTab from './tabs/CalendarTab.svelte';
	import TimerTab from './tabs/TimerTab.svelte';
	import PDTimerTab from './tabs/PDTimerTab.svelte';
	import NewsTab from './tabs/NewsTab.svelte';
	import { currentTab } from '$lib/stores/tabStore.js';
	import { tick } from 'svelte';

	// デバッグ用のリアクティブステートメント
	$: {
		console.log('MainContent: 現在のタブ:', $currentTab);
		// DOMの更新を確実にする
		tick().then(() => {
			console.log('MainContent: DOM更新完了');
		});
	}
</script>

<div class="main-content">
	<TabNavigation />
	
	<div class="content-area" key="{$currentTab}">
		{#if $currentTab === 'spotify'}
			<div>SpotifyTab をレンダリング中...</div>
			<SpotifyTab />
		{:else if $currentTab === 'calendar'}
			<div>CalendarTab をレンダリング中...</div>
			<CalendarTab />
		{:else if $currentTab === 'timer'}
			<div>TimerTab をレンダリング中...</div>
			<TimerTab />
		{:else if $currentTab === 'pdtimer'}
			<div>PDTimerTab をレンダリング中...</div>
			<PDTimerTab />
		{:else if $currentTab === 'news'}
			<div>NewsTab をレンダリング中...</div>
			<NewsTab />
		{:else}
			<div>未知のタブ: {$currentTab}</div>
		{/if}
	</div>
</div>
