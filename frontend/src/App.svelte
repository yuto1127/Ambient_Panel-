<script>
	import { onMount } from 'svelte';
	import StatusPanel from './lib/components/StatusPanel.svelte';
	import MainContent from './lib/components/MainContent.svelte';
	import { currentTab } from './lib/stores/tabStore.js';

	let mounted = false;

	onMount(() => {
		mounted = true;
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
			<div class="text-2xl mb-4">
				<i class="fas fa-spinner fa-spin"></i>
			</div>
			<div class="text-lg">読み込み中...</div>
		</div>
	</div>
{/if}
