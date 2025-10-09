<script>
	import { onMount, onDestroy } from 'svelte';
	import StatusPanel from '$lib/components/StatusPanel.svelte';
	import MainContent from '$lib/components/MainContent.svelte';
	import { currentTab } from '$lib/stores/tabStore.js';

	let mounted = false;
	let timerService = null;

	onMount(async () => {
		mounted = true;
		
		// DOMが完全に読み込まれてからタイマーサービスを初期化
		setTimeout(async () => {
			try {
				// タイマーサービスを動的にインポート
				const { timerService: service } = await import('$lib/services/timerService.js');
				timerService = service;
				
				// タイマーサービスを初期化
				timerService.initialize();
				
				// 通知権限をリクエスト
				await timerService.requestNotificationPermission();
			} catch (error) {
				console.error('App: タイマーサービスの初期化に失敗:', error);
			}
		}, 100);
	});

	onDestroy(() => {
		// タイマーサービスを破棄
		if (timerService) {
			timerService.destroy();
		}
	});
</script>

{#if mounted}
	<div class="container">
		<StatusPanel />
		<MainContent />
	</div>
{:else}
	<div class="flex flex-center" style="height: 100vh;">
		<div class="text-center">
			<div class="text-2xl">
				<i class="fas fa-spinner fa-spin"></i>
			</div>
		</div>
	</div>
{/if}
