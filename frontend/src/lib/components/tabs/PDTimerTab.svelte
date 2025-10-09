<script>
	import { onMount } from 'svelte';
	import { pomodoroTimer, timerSettings } from '$lib/stores/timerStore.js';
	import { timerService } from '$lib/services/timerService.js';

	let showSettingsModal = false;
	let settings = {
		workTime: 25,
		breakTime: 5,
		longBreakTime: 15,
		sessions: 4
	};

	onMount(() => {
		timerService.initialize();
		timerService.requestNotificationPermission();
		
		// 初期設定を読み込み
		const currentSettings = $timerSettings;
		settings = { ...currentSettings };
	});

	function formatTime(seconds) {
		const minutes = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
	}

	function startPomodoroTimer() {
		if ($pomodoroTimer.seconds <= 0) {
			alert('ポモドーロタイマーを開始するには、まず設定を行ってください。');
			return;
		}
		timerService.startPomodoroTimer();
	}

	function pausePomodoroTimer() {
		timerService.pausePomodoroTimer();
	}

	function resetPomodoroTimer() {
		timerService.resetPomodoroTimer();
	}

	function updateSettings() {
		timerService.updatePomodoroSettings(
			settings.workTime,
			settings.breakTime,
			settings.longBreakTime,
			settings.sessions
		);
		showSettingsModal = false;
	}

	function openSettingsModal() {
		const currentSettings = $timerSettings;
		settings = { ...currentSettings };
		showSettingsModal = true;
	}

	function getPhaseText(phase) {
		switch (phase) {
			case 'work':
				return '作業時間';
			case 'break':
				return '休憩時間';
			case 'longBreak':
				return '長い休憩';
			case 'completed':
				return '完了';
			default:
				return '準備中';
		}
	}

	function getPhaseColor(phase) {
		switch (phase) {
			case 'work':
				return 'text-success';
			case 'break':
				return 'text-info';
			case 'longBreak':
				return 'text-primary';
			case 'completed':
				return 'text-warning';
			default:
				return 'text-muted';
		}
	}

	$: displayTime = formatTime($pomodoroTimer.seconds);
	$: isRunning = $pomodoroTimer.isRunning && !$pomodoroTimer.isPaused;
	$: isPaused = $pomodoroTimer.isPaused;
	$: phaseText = getPhaseText($pomodoroTimer.phase);
	$: phaseColor = getPhaseColor($pomodoroTimer.phase);
</script>

<div class="tab-content active">
	<h2 class="text-primary mb-6">ポモドーロタイマー</h2>
	
	<div class="text-center">
		<!-- タイマー表示 -->
		<div class="timer-display font-bold text-primary font-mono mb-8">
			{displayTime}
		</div>
		
		<!-- フェーズ表示 -->
		<div class="phase-display mb-6">
			<h3 class="phase-text font-bold {phaseColor} mb-2">{phaseText}</h3>
			{#if $pomodoroTimer.phase !== 'completed'}
				<p class="session-text text-muted">
					セッション {$pomodoroTimer.sessions}/{$timerSettings.sessions}
				</p>
			{/if}
		</div>
		
		<!-- 状態表示 -->
		<div class="timer-status mb-6">
			{#if $pomodoroTimer.seconds <= 0 && $pomodoroTimer.phase !== 'completed'}
				<p class="text-warning status-text">設定を行ってください</p>
			{:else if isRunning}
				<p class="text-success status-text">タイマー実行中</p>
			{:else if isPaused}
				<p class="text-warning status-text">一時停止中</p>
			{:else if $pomodoroTimer.phase === 'completed'}
				<p class="text-warning status-text">全セッション完了！</p>
			{:else}
				<p class="text-info status-text">準備完了</p>
			{/if}
		</div>
		
		<!-- コントロールボタン -->
		<div class="flex flex-center flex-gap mb-8">
			<button 
				class="btn btn-success btn-lg" 
				class:btn-warning={isRunning}
				disabled={$pomodoroTimer.seconds <= 0 || $pomodoroTimer.phase === 'completed'}
				on:click={isRunning ? pausePomodoroTimer : startPomodoroTimer}
			>
				<i class="fas {isRunning ? 'fa-pause' : 'fa-play'}"></i>
				{isRunning ? '一時停止' : '開始'}
			</button>
			
			<button class="btn btn-danger btn-lg" on:click={resetPomodoroTimer}>
				<i class="fas fa-stop"></i>
				リセット
			</button>
		</div>
		
		<!-- 設定ボタン -->
		<div class="mb-8">
			<button class="btn btn-primary btn-lg mb-4" on:click={openSettingsModal}>
				<i class="fas fa-cog"></i>
				設定
			</button>
		</div>

		<!-- 進捗表示 -->
		{#if $pomodoroTimer.phase !== 'completed'}
			<div class="progress-section mb-8">
				<h3 class="progress-title font-semibold mb-4">進捗</h3>
				<div class="progress-bar">
					<div 
						class="progress-fill" 
						style="width: {($pomodoroTimer.sessions / $timerSettings.sessions) * 100}%"
					></div>
				</div>
				<p class="progress-text text-muted mt-2">
					{$pomodoroTimer.sessions} / {$timerSettings.sessions} セッション完了
				</p>
			</div>
		{/if}
	</div>

	<!-- 設定モーダル -->
	{#if showSettingsModal}
		<div class="modal-overlay" role="button" tabindex="0" on:click={() => showSettingsModal = false} on:keydown={(e) => e.key === 'Escape' && (showSettingsModal = false)}>
			<div class="modal" role="dialog" aria-modal="true" on:click|stopPropagation>
				<div class="modal-header">
					<h3>ポモドーロ設定</h3>
					<button class="modal-close" on:click={() => showSettingsModal = false}>
						<i class="fas fa-times"></i>
					</button>
				</div>
				
				<div class="modal-body">
					<div class="settings-grid">
						<div class="setting-group">
							<label>作業時間（分）</label>
							<div class="input-controls">
								<button 
									class="btn btn-sm btn-secondary"
									on:click={() => settings.workTime = Math.max(1, settings.workTime - 1)}
								>
									<i class="fas fa-minus"></i>
								</button>
								<input 
									type="text" 
									value={settings.workTime} 
									readonly
									class="form-input"
								/>
								<button 
									class="btn btn-sm btn-secondary"
									on:click={() => settings.workTime = Math.min(60, settings.workTime + 1)}
								>
									<i class="fas fa-plus"></i>
								</button>
							</div>
						</div>
						
						<div class="setting-group">
							<label>休憩時間（分）</label>
							<div class="input-controls">
								<button 
									class="btn btn-sm btn-secondary"
									on:click={() => settings.breakTime = Math.max(1, settings.breakTime - 1)}
								>
									<i class="fas fa-minus"></i>
								</button>
								<input 
									type="text" 
									value={settings.breakTime} 
									readonly
									class="form-input"
								/>
								<button 
									class="btn btn-sm btn-secondary"
									on:click={() => settings.breakTime = Math.min(30, settings.breakTime + 1)}
								>
									<i class="fas fa-plus"></i>
								</button>
							</div>
						</div>
						
						<div class="setting-group">
							<label>長い休憩時間（分）</label>
							<div class="input-controls">
								<button 
									class="btn btn-sm btn-secondary"
									on:click={() => settings.longBreakTime = Math.max(1, settings.longBreakTime - 1)}
								>
									<i class="fas fa-minus"></i>
								</button>
								<input 
									type="text" 
									value={settings.longBreakTime} 
									readonly
									class="form-input"
								/>
								<button 
									class="btn btn-sm btn-secondary"
									on:click={() => settings.longBreakTime = Math.min(60, settings.longBreakTime + 1)}
								>
									<i class="fas fa-plus"></i>
								</button>
							</div>
						</div>
						
						<div class="setting-group">
							<label>セッション数</label>
							<div class="input-controls">
								<button 
									class="btn btn-sm btn-secondary"
									on:click={() => settings.sessions = Math.max(1, settings.sessions - 1)}
								>
									<i class="fas fa-minus"></i>
								</button>
								<input 
									type="text" 
									value={settings.sessions} 
									readonly
									class="form-input"
								/>
								<button 
									class="btn btn-sm btn-secondary"
									on:click={() => settings.sessions = Math.min(10, settings.sessions + 1)}
								>
									<i class="fas fa-plus"></i>
								</button>
							</div>
						</div>
					</div>
				</div>
				
				<div class="modal-footer">
					<button class="btn btn-secondary" on:click={() => showSettingsModal = false}>
						キャンセル
					</button>
					<button class="btn btn-primary" on:click={updateSettings}>
						設定を保存
					</button>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.timer-display {
		font-size: 3.5rem;
		text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3);
		line-height: 1.2;
	}
	
	@media (min-width: 768px) {
		.timer-display {
			font-size: 4.5rem;
		}
	}
	
	@media (min-width: 1024px) {
		.timer-display {
			font-size: 5.5rem;
		}
	}
	
	.timer-status .status-text {
		font-weight: 600;
		font-size: 1.3rem;
	}
	
	.phase-display .phase-text {
		font-size: 2rem;
		text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
	}
	
	.phase-display .session-text {
		font-size: 1.3rem;
	}
	
	.progress-section {
		max-width: 500px;
		margin: 0 auto;
	}
	
	.progress-section .progress-title {
		font-size: 1.5rem;
	}
	
	.progress-section .progress-text {
		font-size: 1.1rem;
	}
	
	.progress-bar {
		width: 100%;
		height: 28px;
		background: var(--bg-secondary);
		border-radius: 14px;
		overflow: hidden;
		border: 3px solid var(--border-color);
	}
	
	.progress-fill {
		height: 100%;
		background: linear-gradient(90deg, var(--success-color), var(--primary-color));
		transition: width 0.3s ease;
		border-radius: 11px;
	}
	
	.settings-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}
	
	.setting-group {
		display: flex;
		flex-direction: column;
	}
	
	.setting-group label {
		font-weight: 600;
		margin-bottom: 0.5rem;
		color: var(--text-color);
	}
	
	.input-controls {
		display: flex;
		gap: 0.5rem;
		align-items: center;
		justify-content: center;
	}
	
	.input-controls input {
		width: 80px;
		text-align: center;
		font-size: 1.5rem;
		font-weight: bold;
		cursor: default;
		user-select: none;
		padding: 0.75rem;
	}
	
	.input-controls .btn {
		padding: 0.75rem 1rem;
		min-width: 45px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 1.2rem;
	}
	
	.input-controls .btn i {
		font-size: 1.3rem;
	}
	
	.btn-lg {
		padding: 1rem 2rem;
		font-size: 1.3rem;
		min-width: 150px;
	}
	
	.btn-lg i {
		font-size: 1.5rem;
		margin-right: 0.5rem;
	}
	
	@media (max-width: 768px) {
		.settings-grid {
			grid-template-columns: 1fr;
		}
	}
</style>