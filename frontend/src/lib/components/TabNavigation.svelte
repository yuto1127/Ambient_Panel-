<script>
	import { currentTab } from '$lib/stores/tabStore.js';
	import { tabs } from '$lib/stores/tabStore.js';
	import { tick } from 'svelte';

	async function switchTab(tabId) {
		console.log('TabNavigation: タブを切り替え中:', tabId);
		currentTab.set(tabId);
		
		// DOMの更新を待つ
		await tick();
		
		console.log('TabNavigation: 現在のタブ:', $currentTab);
		console.log('TabNavigation: タブ切り替え完了');
	}
</script>

<div class="tab-navigation">
	{#each tabs as tab}
		<button 
			class="tab-btn" 
			class:active={$currentTab === tab.id}
			on:click={() => switchTab(tab.id)}
		>
			<i class={tab.icon}></i>
			{tab.label}
		</button>
	{/each}
</div>
