<script>
	import { onMount } from 'svelte';
	import { newsData } from '$lib/stores/newsStore.js';
	import { api } from '$lib/utils/api.js';

	onMount(async () => {
		console.log('NewsTab: コンポーネントがマウントされました');
		await loadNews();
	});

	async function loadNews() {
		try {
			const data = await api.getNewsHeadlines();
			if (data.success) {
				newsData.set({
					articles: data.data.articles,
					loading: false,
					error: null
				});
			}
		} catch (error) {
			newsData.update(state => ({
				...state,
				loading: false,
				error: error.message
			}));
		}
	}

	function openNews(url) {
		window.open(url, '_blank');
	}
</script>

<div class="tab-content active">
	<h2 class="text-primary mb-6">最新ニュース</h2>
	
	{#if $newsData.loading}
		<div class="flex flex-center" style="height: 200px;">
			<div class="text-center">
				<div class="text-2xl">
					<i class="fas fa-spinner fa-spin"></i>
				</div>
			</div>
		</div>
	{:else if $newsData.error}
		<div class="text-center text-danger">
			<i class="fas fa-exclamation-triangle mb-2"></i>
			<div>エラー: {$newsData.error}</div>
		</div>
	{:else}
		<div class="flex flex-col gap-5">
			{#each $newsData.articles as article}
				<div 
					class="card cursor-pointer hover:transform hover:-translate-y-1 transition-all duration-300"
					on:click={() => openNews(article.url)}
					on:keydown={(e) => e.key === 'Enter' && openNews(article.url)}
					role="button"
					tabindex="0"
				>
					<div class="card-header">
						<h3 class="card-title text-lg leading-relaxed">
							{article.title}
						</h3>
					</div>
					
					{#if article.description}
						<p class="text-secondary text-sm leading-relaxed mb-3">
							{article.description}
						</p>
					{/if}
					
					<div class="flex flex-between items-center">
						<div class="text-muted text-xs">
							{article.source}
						</div>
						{#if article.published_at}
							<div class="text-muted text-xs">
								{new Date(article.published_at).toLocaleDateString('ja-JP')}
							</div>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
