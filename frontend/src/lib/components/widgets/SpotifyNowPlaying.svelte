<script>
	import { onMount, onDestroy } from 'svelte';
	import { spotifyStatus } from '$lib/stores/spotifyStore.js';
	import { api } from '$lib/utils/api.js';

	let interval;

	onMount(async () => {
		// Spotify状態の取得
		await loadSpotifyStatus();
		
		// 定期的な更新（30秒間隔に変更）
		interval = setInterval(loadSpotifyStatus, 30000);
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
				spotifyStatus.set({
					isPlaying: data.is_playing,
					track: data.track,
					device: data.device,
					loading: false,
					error: null
				});
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
			await api.playTrack();
			await loadSpotifyStatus();
		} catch (error) {
			console.error('再生制御に失敗:', error);
		}
	}

	async function previousTrack() {
		try {
			await api.previousTrack();
			await loadSpotifyStatus();
		} catch (error) {
			console.error('前の曲への切り替えに失敗:', error);
		}
	}

	async function nextTrack() {
		try {
			await api.nextTrack();
			await loadSpotifyStatus();
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
		<div class="track-display flex items-center gap-4 mb-4">
			<div class="album-art" style="width: 60px; height: 60px; background: #404040; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #8a8a8a; font-size: 0.8em;">
				サムネイル
			</div>
			<div class="track-info flex-1">
				<div class="track-name text-sm font-bold text-primary mb-1">
					{$spotifyStatus.track?.name || '曲名'}
				</div>
				<div class="artist-name text-xs text-secondary">
					{$spotifyStatus.track?.artists?.[0]?.name || 'アーティスト名'}
				</div>
			</div>
		</div>
		
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
		
		<div class="controls flex justify-center gap-4">
			<button 
				class="control-btn text-white hover:text-green-400 transition-colors"
				on:click={previousTrack}
			>
				<i class="fas fa-step-backward"></i>
			</button>
			
			<button 
				class="control-btn text-white hover:text-green-400 transition-colors"
				on:click={togglePlayback}
			>
				<i class="fas fa-play"></i>
			</button>
			
			<button 
				class="control-btn text-white hover:text-green-400 transition-colors"
				on:click={nextTrack}
			>
				<i class="fas fa-step-forward"></i>
			</button>
		</div>
	</div>
</div>
