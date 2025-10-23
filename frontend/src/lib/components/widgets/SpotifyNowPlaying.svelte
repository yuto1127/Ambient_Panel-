<script>
	import { onMount, onDestroy } from 'svelte';
	import { spotifyStatus } from '$lib/stores/spotifyStore.js';
	import { api } from '$lib/utils/api.js';

	let interval;

	onMount(async () => {
		// Spotify状態の取得
		await loadSpotifyStatus();
		
		// 定期的な更新（5秒間隔に短縮）
		interval = setInterval(loadSpotifyStatus, 5000);
	});

	onDestroy(() => {
		if (interval) {
			clearInterval(interval);
		}
	});

	async function loadSpotifyStatus() {
		try {
			const data = await api.getCurrentPlayback();
			if (data.success) {
				spotifyStatus.update(currentState => ({
					...currentState, // 既存の状態（認証状態など）を保持
					isPlaying: data.is_playing,
					track: {
						...data.track,
						progress_ms: data.progress_ms || 0,
						duration_ms: data.track?.duration_ms || 0
					},
					device: {
						name: data.device_name || 'Ambient Panel',
						volume_percent: data.volume || 50
					},
					loading: false,
					error: null
				}));
			}
		} catch (error) {
			spotifyStatus.update(state => ({
				...state,
				loading: false,
				error: error.message
			}));
		}
	}

	async function togglePlayback() {
		try {
			if ($spotifyStatus.isPlaying) {
				await api.pausePlayback();
			} else {
				// 再生を開始（現在の曲をそのまま再生）
				await api.playTrack();
			}
			// 即座に状態を更新
			setTimeout(loadSpotifyStatus, 500);
		} catch (error) {
			console.error('再生制御に失敗:', error);
		}
	}

	async function previousTrack() {
		try {
			console.log('前の曲ボタンが押されました');
			const result = await api.previousTrack();
			console.log('前の曲の結果:', result);
			
			if (result.success) {
				// 即座に状態を更新
				setTimeout(loadSpotifyStatus, 500);
			} else {
				console.error('前の曲への切り替えに失敗:', result.error);
			}
		} catch (error) {
			console.error('前の曲への切り替えに失敗:', error);
		}
	}

	async function nextTrack() {
		try {
			console.log('次の曲ボタンが押されました');
			const result = await api.nextTrack();
			console.log('次の曲の結果:', result);
			
			if (result.success) {
				// 即座に状態を更新
				setTimeout(loadSpotifyStatus, 500);
			} else {
				console.error('次の曲への切り替えに失敗:', result.error);
			}
		} catch (error) {
			console.error('次の曲への切り替えに失敗:', error);
		}
	}

	$: progressPercentage = $spotifyStatus.track?.duration_ms > 0 
		? ($spotifyStatus.track.progress_ms / $spotifyStatus.track.duration_ms) * 100 
		: 0;
</script>

<div class="widget spotify-now-playing">
	<div class="spotify-content">
		<!-- 曲名とアーティスト名の表示 -->
		<div class="track-info mb-4">
			<div class="track-name text-sm font-bold text-primary mb-1">
				{$spotifyStatus.track?.name || '曲名'}
			</div>
			<div class="artist-name text-xs text-secondary">
				{$spotifyStatus.track?.artists?.[0]?.name || 'アーティスト名'}
			</div>
		</div>
		
		<!-- 再生バー -->
		<div class="progress-bar mb-4" style="width: 100%; height: 4px; background: #404040; border-radius: 2px; overflow: hidden; position: relative;">
			<div 
				class="progress" 
				style="height: 100%; background: #1db954; width: {progressPercentage}%; transition: width 0.3s ease;"
			></div>
			<div 
				class="progress-handle" 
				style="position: absolute; top: -2px; left: {progressPercentage}%; width: 8px; height: 8px; background: white; border-radius: 50%;"
			></div>
		</div>
		
		<!-- コントロールボタン -->
		<div class="controls flex justify-between items-center">
			<button 
				class="control-btn text-white hover:text-green-400 transition-colors"
				on:click={previousTrack}
				title="前の曲"
			>
				<i class="fas fa-step-backward"></i>
			</button>
			
			<button 
				class="control-btn text-white hover:text-green-400 transition-colors"
				on:click={togglePlayback}
				title={$spotifyStatus.isPlaying ? '一時停止' : '再生'}
			>
				<i class="fas {$spotifyStatus.isPlaying ? 'fa-pause' : 'fa-play'}"></i>
			</button>
			
			<button 
				class="control-btn text-white hover:text-green-400 transition-colors"
				on:click={nextTrack}
				title="次の曲"
			>
				<i class="fas fa-step-forward"></i>
			</button>
		</div>
	</div>
</div>
