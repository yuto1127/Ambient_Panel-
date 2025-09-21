<script>
	import { onMount } from 'svelte';
	import { playlists } from '$lib/stores/spotifyStore.js';

	let mockPlaylists = [
		{
			id: 'mock_1',
			name: 'お気に入りミュージック',
			track_count: 25,
			description: 'よく聞く楽曲を集めたプレイリスト'
		},
		{
			id: 'mock_2',
			name: '作業用BGM',
			track_count: 18,
			description: '集中して作業するための音楽'
		},
		{
			id: 'mock_3',
			name: 'リラックス音楽',
			track_count: 32,
			description: 'ゆったりとした時間に聴く音楽'
		},
		{
			id: 'mock_4',
			name: 'アップテンポ',
			track_count: 28,
			description: '気分を上げたい時の音楽'
		},
		{
			id: 'mock_5',
			name: 'クラシック',
			track_count: 15,
			description: 'クラシック音楽の名曲集'
		}
	];

	onMount(() => {
		console.log('SpotifyTab: コンポーネントがマウントされました');
		// モックデータをストアに設定
		playlists.set({
			items: mockPlaylists,
			loading: false,
			error: null
		});
	});

	function selectPlaylist(playlistId) {
		console.log('プレイリスト選択:', playlistId);
		// モック実装: 選択されたプレイリストの情報を表示
		const playlist = mockPlaylists.find(p => p.id === playlistId);
		if (playlist) {
			alert(`プレイリスト「${playlist.name}」を選択しました\n曲数: ${playlist.track_count}曲\n説明: ${playlist.description}`);
		}
	}
</script>

<div class="tab-content active">
	<div class="flex items-center justify-between mb-6">
		<h2 class="text-primary">Spotify プレイリスト</h2>
		<div class="text-sm text-gray-400 bg-gray-800 px-3 py-1 rounded-full">
			<i class="fas fa-info-circle mr-1"></i>
			モックデータ
		</div>
	</div>
	
	<div class="mb-4 p-4 bg-blue-900 bg-opacity-30 border border-blue-500 border-opacity-30 rounded-lg">
		<div class="flex items-center">
			<i class="fas fa-music text-blue-400 mr-3"></i>
			<div>
				<h3 class="text-blue-300 font-semibold mb-1">Spotify機能について</h3>
				<p class="text-gray-300 text-sm">
					現在はモックデータを表示しています。実際のSpotify連携機能は今後実装予定です。
				</p>
			</div>
		</div>
	</div>
	
	{#if $playlists.loading}
		<div class="flex flex-center" style="height: 200px;">
			<div class="text-center">
				<div class="text-2xl mb-4">
					<i class="fas fa-spinner fa-spin"></i>
				</div>
				<div class="text-lg">読み込み中...</div>
			</div>
		</div>
	{:else if $playlists.error}
		<div class="text-center text-danger">
			<i class="fas fa-exclamation-triangle mb-2"></i>
			<div>エラー: {$playlists.error}</div>
		</div>
	{:else}
		<div class="playlist-list">
			{#each $playlists.items as playlist}
				<div 
					class="playlist-item flex items-center gap-4 p-4 bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-700 transition-colors mb-3"
					on:click={() => selectPlaylist(playlist.id)}
					on:keydown={(e) => e.key === 'Enter' && selectPlaylist(playlist.id)}
					role="button"
					tabindex="0"
				>
					<div class="playlist-thumbnail flex-shrink-0" style="width: 60px; height: 60px; background: linear-gradient(135deg, #1db954, #1ed760); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.2em;">
						<i class="fab fa-spotify"></i>
					</div>
					<div class="playlist-info flex-1">
						<h3 class="text-white font-bold mb-1">{playlist.name}</h3>
						<p class="text-gray-400 text-sm mb-1">{playlist.track_count}曲</p>
						<p class="text-gray-500 text-xs">{playlist.description}</p>
					</div>
					<div class="playlist-action text-gray-400 hover:text-white transition-colors">
						<i class="fas fa-play"></i>
					</div>
				</div>
			{/each}
		</div>
		
		<div class="mt-6 p-4 bg-gray-800 rounded-lg">
			<h3 class="text-white font-semibold mb-2">
				<i class="fas fa-lightbulb mr-2"></i>
				今後の実装予定
			</h3>
			<ul class="text-gray-300 text-sm space-y-1">
				<li>• Spotify Web APIとの連携</li>
				<li>• プレイリストの実際の再生</li>
				<li>• 現在再生中の楽曲の表示</li>
				<li>• 音量調整とコントロール</li>
			</ul>
		</div>
	{/if}
</div>
