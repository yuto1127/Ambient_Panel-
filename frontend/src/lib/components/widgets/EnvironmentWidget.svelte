<script>
	import { onMount, onDestroy } from 'svelte';
	import { environmentData } from '$lib/stores/environmentStore.js';
	import { api } from '$lib/utils/api.js';

	let interval;

	onMount(async () => {
		// 環境データの取得
		await loadEnvironmentData();
		
		// 定期的な更新（30秒間隔でより頻繁に更新）
		interval = setInterval(loadEnvironmentData, 30000);
	});

	onDestroy(() => {
		if (interval) {
			clearInterval(interval);
		}
	});

	async function loadEnvironmentData() {
		try {
			console.log('🔍 Loading environment data...');
			const data = await api.getEnvironmentData();
			console.log('📊 Environment API response:', data);
			
			if (data.success) {
				const envData = {
					temperature: data.data.temperature || 0,
					humidity: data.data.humidity || 0,
					co2: data.data.co2 || 0,
					loading: false,
					error: data.data.error || null,
					note: data.data.note || null,
					lastUpdated: new Date().toLocaleTimeString('ja-JP')
				};
				
				console.log('✅ Setting environment data:', envData);
				environmentData.set(envData);
			} else {
				console.error('❌ API returned success: false');
				environmentData.update(state => ({
					...state,
					loading: false,
					error: 'API returned success: false'
				}));
			}
		} catch (error) {
			console.error('❌ Error loading environment data:', error);
			environmentData.update(state => ({
				...state,
				loading: false,
				error: error.message
			}));
		}
	}
</script>

<div class="widget environment">
	<div class="env-data">
		{#if $environmentData.loading}
			<div class="text-center text-secondary">読み込み中...</div>
		{:else if $environmentData.error}
			<div class="text-center text-red-500">
				<div class="text-sm">エラー: {$environmentData.error}</div>
				<button 
					class="mt-2 px-3 py-1 bg-blue-500 text-white rounded text-xs"
					on:click={loadEnvironmentData}
				>
					再試行
				</button>
			</div>
		{:else}
			<div class="env-main flex items-center justify-between mb-3">
				<div class="env-label text-sm text-secondary">室内</div>
				<div class="env-values text-lg font-bold text-primary">
					{$environmentData.temperature}℃ / {$environmentData.humidity}%
				</div>
			</div>
			
			<div class="env-co2 flex items-center justify-between">
				<div class="co2-label text-sm text-secondary">CO2:</div>
				<div class="co2-value text-lg font-bold text-primary">
					{$environmentData.co2} ppm
				</div>
			</div>
			
			{#if $environmentData.note}
				<div class="env-note text-xs text-gray-500 mt-2 text-center">
					{$environmentData.note}
				</div>
			{/if}
			
			{#if $environmentData.lastUpdated}
				<div class="env-updated text-xs text-gray-400 mt-1 text-center">
					更新: {$environmentData.lastUpdated}
				</div>
			{/if}
		{/if}
	</div>
</div>
