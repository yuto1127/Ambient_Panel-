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

	function getCO2Status(co2) {
		if (co2 >= 2000) {
			return { label: '危険', color: '#dc2626', icon: 'fa-exclamation-triangle', bgColor: '#fee2e2' };
		} else if (co2 >= 1000) {
			return { label: '要注意', color: '#f97316', icon: 'fa-exclamation-circle', bgColor: '#ffedd5' };
		} else if (co2 >= 700) {
			return { label: '注意', color: '#eab308', icon: 'fa-info-circle', bgColor: '#fef9c3' };
		} else if (co2 >= 450) {
			return { label: '通常', color: '#3b82f6', icon: 'fa-check-circle', bgColor: '#dbeafe' };
		} else if (co2 >= 350) {
			return { label: '最適', color: '#10b981', icon: 'fa-check-circle', bgColor: '#d1fae5' };
		} else {
			return { label: '低い', color: '#6b7280', icon: 'fa-question-circle', bgColor: '#f3f4f6' };
		}
	}

	$: co2Status = getCO2Status($environmentData.co2);
</script>

<div class="widget environment">
	<div class="env-data">
		{#if $environmentData.loading}
			<div class="text-center text-secondary">
				<i class="fas fa-spinner fa-spin"></i>
			</div>
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
			
			<div class="env-co2">
				<div class="flex items-center justify-between mb-2">
					<div class="co2-label text-sm text-secondary">CO2:</div>
					<div class="co2-value text-lg font-bold text-primary">
						{$environmentData.co2} ppm
					</div>
				</div>
				<div class="co2-status-badge" style="background-color: {co2Status.bgColor}; border-left: 4px solid {co2Status.color};">
					<i class="fas {co2Status.icon}" style="color: {co2Status.color};"></i>
					<span class="status-label" style="color: {co2Status.color};">{co2Status.label}</span>
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

<style>
	.co2-status-badge {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
		border-radius: 0.375rem;
		font-size: 0.875rem;
		font-weight: 600;
		transition: all 0.3s ease;
	}

	.co2-status-badge i {
		font-size: 1rem;
	}

	.status-label {
		font-weight: 700;
	}

	.env-co2 {
		margin-top: 0.5rem;
	}
</style>
