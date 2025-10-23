<script>
	import { onMount } from 'svelte';
	import { playlists, spotifyStatus } from '$lib/stores/spotifyStore.js';

	let authUrl = '';
	let isAuthenticated = false;
	let selectedPlaylist = null;
	let playlistTracks = [];
	let loadingTracks = false;
	let availableDevices = [];
	let selectedDevice = null;
	
	// spotifyStatusストアの変更を監視
	$: {
		isAuthenticated = $spotifyStatus?.authenticated || false;
		console.log('SpotifyTab: 認証状態が更新されました:', {
			spotifyStatus: $spotifyStatus,
			isAuthenticated: isAuthenticated
		});
	}

	onMount(async () => {
		console.log('SpotifyTab: コンポーネントがマウントされました');
		await loadSpotifyData();
		await loadDevices();
	});

	async function loadSpotifyData() {
		console.log('Spotify data loading started...');
		try {
			// Spotify認証状態を確認
			console.log('Fetching Spotify status...');
			const statusResponse = await fetch('/api/spotify/status');
			const statusData = await statusResponse.json();
			console.log('Spotify status:', statusData);
			
			console.log('SpotifyTab: ストアを更新中:', statusData);
			spotifyStatus.update(currentState => ({
				...currentState, // 既存の状態を保持
				...statusData, // 新しい状態で上書き
				loading: false,
				error: null
			}));
			console.log('SpotifyTab: ストア更新後の状態:', $spotifyStatus);
			
			// ローカル変数も直接更新
			isAuthenticated = statusData.authenticated || false;
			console.log('SpotifyTab: ローカル認証状態を更新:', isAuthenticated);

			if (statusData.authenticated) {
				// プレイリストを取得
				console.log('Fetching playlists...');
				const playlistsResponse = await fetch('/api/spotify/playlists');
				const playlistsData = await playlistsResponse.json();
				console.log('Playlists data:', playlistsData);
				
				if (playlistsData.success) {
					const playlistItems = playlistsData.playlists || [];
					console.log(`Found ${playlistItems.length} playlists`);
					playlists.set({
						items: playlistItems,
						loading: false,
						error: null
					});
				} else {
					console.error('Playlists fetch failed:', playlistsData);
					playlists.set({
						items: [],
						loading: false,
						error: playlistsData.error || 'プレイリストの取得に失敗しました'
					});
				}
			} else {
				// 認証URLを取得
				console.log('Not authenticated, getting auth URL...');
				const authResponse = await fetch('/api/spotify/auth');
				const authData = await authResponse.json();
				
				if (authData.success) {
					authUrl = authData.auth_url;
				}
				
				// ローカル変数も更新
				isAuthenticated = false;
				console.log('SpotifyTab: 認証されていないため、ローカル状態をfalseに設定');
				
				playlists.set({
					items: [],
					loading: false,
					error: 'Spotifyに認証が必要です'
				});
			}
		} catch (error) {
			console.error('Spotify data loading error:', error);
			playlists.set({
				items: [],
				loading: false,
				error: 'データの取得に失敗しました'
			});
		}
	}

	async function loadDevices() {
		console.log('Loading devices...');
		try {
			const response = await fetch('/api/spotify/devices');
			const result = await response.json();
			
			if (result.success) {
				availableDevices = result.data.devices || [];
				// アクティブなデバイスを選択
				selectedDevice = availableDevices.find(d => d.is_active) || availableDevices[0] || null;
				console.log(`Found ${availableDevices.length} devices, selected:`, selectedDevice?.name);
			} else {
				console.error('Failed to load devices:', result.error);
				availableDevices = [];
			}
		} catch (error) {
			console.error('Error loading devices:', error);
			availableDevices = [];
		}
	}

	async function selectPlaylist(playlistId) {
		console.log('プレイリスト選択:', playlistId);
		
		if (!isAuthenticated) {
			alert('Spotifyに認証してください');
			return;
		}
		
		// 選択されたプレイリストを設定
		selectedPlaylist = $playlists.items.find(p => p.id === playlistId);
		playlistTracks = [];
		loadingTracks = true;
		
		try {
			// プレイリストの詳細（曲の一覧）を取得
			const response = await fetch(`/api/spotify/playlists/${playlistId}`);
			const result = await response.json();
			
			console.log('プレイリスト詳細結果:', result);
			
			if (result.success) {
				playlistTracks = result.tracks || [];
				console.log(`${playlistTracks.length}曲を取得しました`);
			} else {
				console.error('プレイリストの詳細取得に失敗:', result.error);
				playlistTracks = [];
				alert(`プレイリストの詳細取得に失敗しました: ${result.error}`);
			}
		} catch (error) {
			console.error('プレイリスト詳細取得エラー:', error);
			playlistTracks = [];
			alert('エラーが発生しました');
		} finally {
			loadingTracks = false;
		}
	}
	
	async function playPlaylist(playlistId) {
		console.log('プレイリスト再生:', playlistId);
		
		try {
			// プレイリストを再生
			const response = await fetch(`/api/spotify/play?playlist_id=${playlistId}`, {
				method: 'POST'
			});
			
			const result = await response.json();
			console.log('プレイリスト再生結果:', result);
			
			if (result.success) {
				// 成功時はポップアップを表示しない（空のレスポンスは正常）
				console.log('プレイリストの再生を開始しました');
			} else {
				// エラーメッセージを改善
				let errorMessage = result.error;
				if (errorMessage.includes('No active device found')) {
					errorMessage = 'アクティブなデバイスが見つかりません。Spotifyアプリで音楽を再生してから試してください。';
				} else if (errorMessage.includes('unexpected mimetype')) {
					errorMessage = '再生コマンドが送信されましたが、レスポンスの形式が予期されないものでした。実際には再生されている可能性があります。';
				}
				alert(`再生に失敗しました: ${errorMessage}`);
			}
		} catch (error) {
			console.error('プレイリスト再生エラー:', error);
			alert('エラーが発生しました');
		}
	}
	
	async function playTrack(trackUri) {
		console.log('楽曲再生:', trackUri);
		
		try {
			// 楽曲を再生
			const response = await fetch(`/api/spotify/play?track_uri=${trackUri}`, {
				method: 'POST'
			});
			
			const result = await response.json();
			console.log('楽曲再生結果:', result);
			
			if (result.success) {
				// 成功時はポップアップを表示しない（空のレスポンスは正常）
				console.log('楽曲の再生を開始しました');
			} else {
				// エラーメッセージを改善
				let errorMessage = result.error;
				if (errorMessage.includes('No active device found')) {
					errorMessage = 'アクティブなデバイスが見つかりません。Spotifyアプリで音楽を再生してから試してください。';
				} else if (errorMessage.includes('unexpected mimetype')) {
					errorMessage = '再生コマンドが送信されましたが、レスポンスの形式が予期されないものでした。実際には再生されている可能性があります。';
				}
				alert(`再生に失敗しました: ${errorMessage}`);
			}
		} catch (error) {
			console.error('楽曲再生エラー:', error);
			alert('エラーが発生しました');
		}
	}
	
	function formatDuration(durationMs) {
		const minutes = Math.floor(durationMs / 60000);
		const seconds = Math.floor((durationMs % 60000) / 1000);
		return `${minutes}:${seconds.toString().padStart(2, '0')}`;
	}
	
	function goBackToPlaylists() {
		selectedPlaylist = null;
		playlistTracks = [];
	}

	function openAuthUrl() {
		if (authUrl) {
			window.open(authUrl, '_blank');
		}
	}
</script>

<div class="tab-content active">
	{#if selectedPlaylist}
		<!-- プレイリスト詳細表示 -->
		<div class="flex items-center justify-between mb-6">
			<div class="flex items-center gap-4">
				<button 
					class="text-gray-400 hover:text-white transition-colors"
					on:click={goBackToPlaylists}
				>
					<i class="fas fa-arrow-left text-xl"></i>
				</button>
				<h2 class="text-primary">{selectedPlaylist.name}</h2>
			</div>
			<button 
				class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
				on:click={() => playPlaylist(selectedPlaylist.id)}
			>
				<i class="fas fa-play mr-2"></i>
				再生
			</button>
		</div>
		
		<div class="mb-4 text-sm text-gray-400">
			{selectedPlaylist.description || '説明なし'} - {selectedPlaylist.tracks_total}曲
		</div>
		
		{#if availableDevices.length > 0}
			<div class="mb-4 p-3 bg-gray-800 rounded-lg">
				<div class="text-sm text-gray-300 mb-2">再生デバイス:</div>
				<select 
					class="w-full bg-gray-700 text-white p-2 rounded border border-gray-600"
					bind:value={selectedDevice}
					on:change={() => console.log('Device selected:', selectedDevice?.name)}
				>
					{#each availableDevices as device}
						<option value={device} selected={device.is_active}>
							{device.name} {device.is_active ? '(アクティブ)' : ''}
						</option>
					{/each}
				</select>
				{#if selectedDevice && !selectedDevice.is_active}
					<div class="text-xs text-yellow-400 mt-2">
						⚠️ このデバイスは現在アクティブではありません。Spotifyアプリで音楽を再生してから試してください。
					</div>
				{/if}
			</div>
		{:else}
			<div class="mb-4 p-3 bg-yellow-900 bg-opacity-30 border border-yellow-500 border-opacity-30 rounded-lg">
				<div class="text-yellow-300 text-sm">
					⚠️ 利用可能なデバイスが見つかりません。SpotifyアプリまたはWebプレイヤーで音楽を再生してから試してください。
				</div>
			</div>
		{/if}
		
		{#if loadingTracks}
			<div class="flex justify-center py-8">
				<div class="text-center">
					<div class="text-2xl mb-2">
						<i class="fas fa-spinner fa-spin"></i>
					</div>
					<div class="text-gray-400">曲を読み込み中...</div>
				</div>
			</div>
		{:else if playlistTracks.length === 0}
			<div class="text-center text-gray-400 py-8">
				<i class="fas fa-music mb-2 text-2xl"></i>
				<div>曲が見つかりません</div>
			</div>
		{:else}
			<div class="tracks-container" style="max-height: 60vh; overflow-y: auto; padding-right: 8px;">
				<!-- テーブルヘッダー -->
				<div class="track-table-header grid grid-cols-12 gap-4 px-4 py-2 text-gray-400 text-sm border-b border-gray-700 mb-2">
					<div class="col-span-1 text-center">#</div>
					<div class="col-span-6">タイトル</div>
					<div class="col-span-3">アルバム</div>
					<div class="col-span-2 text-right">
						<i class="fas fa-clock"></i>
					</div>
				</div>
				
				<!-- 楽曲リスト -->
				<div class="space-y-1">
					{#each playlistTracks as track, index}
						{@const isCurrentlyPlaying = $spotifyStatus?.track?.uri === track.uri}
						<div 
							class="track-row grid grid-cols-12 gap-4 px-4 py-3 rounded-lg transition-colors cursor-pointer group {isCurrentlyPlaying ? 'bg-gray-800' : 'hover:bg-gray-800'}"
							on:click={() => playTrack(track.uri)}
						>
							<!-- 番号 -->
							<div class="col-span-1 flex items-center justify-center">
								{#if isCurrentlyPlaying}
									<div class="playing-indicator text-green-400">
										<i class="fas fa-volume-up text-sm"></i>
									</div>
								{:else}
									<div class="track-number text-gray-400 text-sm group-hover:hidden">
										{index + 1}
									</div>
									<div class="play-icon hidden group-hover:block text-white">
										<i class="fas fa-play text-sm"></i>
									</div>
								{/if}
							</div>
							
							<!-- タイトルとアーティスト -->
							<div class="col-span-6 flex items-center gap-3">
								<div class="track-info flex-1 min-w-0">
									<div class="track-name {isCurrentlyPlaying ? 'text-green-400' : 'text-white'} font-medium truncate">
										{track.name}
									</div>
									<div class="track-artist text-gray-400 text-sm truncate">
										{track.artists.join(', ')}
									</div>
								</div>
							</div>
							
							<!-- アルバム -->
							<div class="col-span-3 flex items-center">
								<div class="track-album text-gray-400 text-sm truncate">
									{track.album}
								</div>
							</div>
							
							<!-- 再生時間 -->
							<div class="col-span-2 flex items-center justify-end">
								<div class="track-duration text-gray-400 text-sm">
									{formatDuration(track.duration_ms)}
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	{:else}
		<!-- プレイリスト一覧表示 -->
		<div class="flex items-center justify-between mb-6">
			<h2 class="text-primary">Spotify プレイリスト</h2>
			{#if isAuthenticated}
				<div class="text-sm text-green-400 bg-green-900 bg-opacity-30 px-3 py-1 rounded-full">
					<i class="fas fa-check-circle mr-1"></i>
					認証済み
				</div>
			{:else}
				<div class="text-sm text-yellow-400 bg-yellow-900 bg-opacity-30 px-3 py-1 rounded-full">
					<i class="fas fa-exclamation-triangle mr-1"></i>
					未認証
				</div>
			{/if}
		</div>
	
	{#if !isAuthenticated}
		<div class="mb-4 p-4 bg-yellow-900 bg-opacity-30 border border-yellow-500 border-opacity-30 rounded-lg">
			<div class="flex items-center justify-between">
				<div class="flex items-center">
					<i class="fas fa-key text-yellow-400 mr-3"></i>
					<div>
						<h3 class="text-yellow-300 font-semibold mb-1">Spotify認証が必要です</h3>
						<p class="text-gray-300 text-sm">
							Spotifyのプレイリストを表示するには、まず認証を行ってください。
						</p>
					</div>
				</div>
				{#if authUrl}
					<button 
						class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
						on:click={openAuthUrl}
					>
						<i class="fab fa-spotify mr-2"></i>
						認証する
					</button>
				{/if}
			</div>
		</div>
	{/if}
	
	{#if $playlists.loading}
		<div class="flex flex-center" style="height: 200px;">
			<div class="text-center">
				<div class="text-2xl mb-2">
					<i class="fas fa-spinner fa-spin"></i>
				</div>
				<div class="text-gray-400">プレイリストを読み込み中...</div>
			</div>
		</div>
	{:else if $playlists.error}
		<div class="text-center text-red-400 p-4">
			<i class="fas fa-exclamation-triangle mb-2 text-2xl"></i>
			<div>エラー: {$playlists.error}</div>
			<button 
				class="mt-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
				on:click={loadSpotifyData}
			>
				再試行
			</button>
		</div>
	{:else if $playlists.items.length === 0}
		<div class="text-center text-gray-400 p-4">
			<i class="fas fa-music mb-2 text-2xl"></i>
			<div>プレイリストが見つかりません</div>
		</div>
	{:else}
		<div class="playlist-list">
			<div class="text-sm text-gray-400 mb-3">
				{isAuthenticated ? '認証済み' : '未認証'} - {$playlists.items.length}件のプレイリスト
			</div>
			<div class="playlists-container" style="max-height: 70vh; overflow-y: auto; padding-right: 8px;">
				{#each $playlists.items as playlist}
					<div class="playlist-item bg-gray-800 rounded-lg mb-3 overflow-hidden">
						<div 
							class="flex items-center gap-4 p-4 cursor-pointer hover:bg-gray-700 transition-colors"
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
								<p class="text-gray-400 text-sm mb-1">{playlist.tracks_total}曲</p>
								{#if playlist.description}
									<p class="text-gray-500 text-xs">{playlist.description}</p>
								{/if}
							</div>
							<div class="playlist-action text-gray-400 hover:text-white transition-colors">
								<i class="fas fa-list"></i>
							</div>
						</div>
						<div class="playlist-controls flex justify-end gap-2 p-2 bg-gray-750 border-t border-gray-700">
							<button 
								class="text-gray-400 hover:text-white transition-colors px-3 py-1 text-sm"
								on:click={(e) => { e.stopPropagation(); selectPlaylist(playlist.id); }}
							>
								<i class="fas fa-list mr-1"></i>
								詳細
							</button>
							<button 
								class="text-green-400 hover:text-green-300 transition-colors px-3 py-1 text-sm"
								on:click={(e) => { e.stopPropagation(); playPlaylist(playlist.id); }}
							>
								<i class="fas fa-play mr-1"></i>
								再生
							</button>
						</div>
					</div>
				{/each}
			</div>
		</div>
		
	{/if}
	{/if}
</div>

<style>
	.tracks-container::-webkit-scrollbar,
	.playlists-container::-webkit-scrollbar {
		width: 8px;
	}
	
	.tracks-container::-webkit-scrollbar-track,
	.playlists-container::-webkit-scrollbar-track {
		background: #374151;
		border-radius: 4px;
	}
	
	.tracks-container::-webkit-scrollbar-thumb,
	.playlists-container::-webkit-scrollbar-thumb {
		background: #6b7280;
		border-radius: 4px;
	}
	
	.tracks-container::-webkit-scrollbar-thumb:hover,
	.playlists-container::-webkit-scrollbar-thumb:hover {
		background: #9ca3af;
	}
	
	.track-table-header {
		position: sticky;
		top: 0;
		background: rgba(17, 24, 39, 0.95);
		backdrop-filter: blur(8px);
		z-index: 10;
	}
	
	.track-row {
		transition: all 0.2s ease-in-out;
	}
	
	.track-row:hover {
		background-color: rgba(31, 41, 55, 0.8);
	}
	
	.playing-indicator {
		animation: pulse 2s infinite;
	}
	
	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}
	
	.track-name {
		transition: color 0.2s ease-in-out;
	}
	
	.track-row:hover .track-name {
		color: #ffffff;
	}
</style>
