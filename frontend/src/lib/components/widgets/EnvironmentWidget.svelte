<script>
	import { onMount, onDestroy } from 'svelte';
	import { environmentData } from '$lib/stores/environmentStore.js';
	import { api } from '$lib/utils/api.js';

	let interval;

	onMount(async () => {
		// 環境データの取得
		await loadEnvironmentData();
		
		// 定期的な更新（60秒間隔に変更）
		interval = setInterval(loadEnvironmentData, 60000);
	});

	onDestroy(() => {
		if (interval) {
			clearInterval(interval);
		}
	});

	async function loadEnvironmentData() {
		try {
			const data = await api.getEnvironmentData();
			if (data.success) {
				environmentData.set({
					temperature: data.data.temperature,
					humidity: data.data.humidity,
					co2: data.data.co2,
					loading: false,
					error: null
				});
			}
		} catch (error) {
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
		<div class="env-main flex items-center justify-between mb-3">
			<div class="env-label text-sm text-secondary">室内</div>
			<div class="env-values text-lg font-bold text-primary">
				{$environmentData.temperature}℃ / {$environmentData.humidity}%
			</div>
		</div>
		
		<div class="env-co2 flex items-center justify-between">
			<div class="co2-label text-sm text-secondary">CO2:</div>
			<div class="co2-value text-lg font-bold text-primary">
				{$environmentData.co2}
			</div>
		</div>
	</div>
</div>
