<script>
	import { onMount } from 'svelte';
	import { timer, customTimerSettings } from '$lib/stores/timerStore.js';
	import { timerService } from '$lib/services/timerService.js';
	import { formatDuration } from '$lib/utils/dateTime.js';

	let showTimeModal = false;
	let showSettingsModal = false;
	let timeInput = {
		hours: 0,
		minutes: 0,
		seconds: 0
	};

	onMount(() => {
		timerService.initialize();
		timerService.requestNotificationPermission();
	});

	function formatTime(seconds) {
		const hours = Math.floor(seconds / 3600);
		const minutes = Math.floor((seconds % 3600) / 60);
		const secs = seconds % 60;
		
		if (hours > 0) {
			return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
		} else {
			return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
		}
	}

	function startTimer() {
		if ($timer.seconds <= 0) {
			alert('タイマーを開始するには、まず時間を設定してください。');
			return;
		}
		timerService.startTimer();
	}

	function pauseTimer() {
		timerService.pauseTimer();
	}

	function resetTimer() {
		timerService.resetTimer();
	}

	function setTime() {
		const totalSeconds = timeInput.hours * 3600 + timeInput.minutes * 60 + timeInput.seconds;
		if (totalSeconds <= 0) {
			alert('時間を正しく設定してください。');
			return;
		}
		
		timerService.setTimerTime(timeInput.hours, timeInput.minutes, timeInput.seconds);
		showTimeModal = false;
		timeInput = { hours: 0, minutes: 0, seconds: 0 };
	}

	function openTimeModal() {
		timeInput = { hours: 0, minutes: 0, seconds: 0 };
		showTimeModal = true;
	}


	$: displayTime = formatTime($timer.seconds);
	$: isRunning = $timer.isRunning && !$timer.isPaused;
	$: isPaused = $timer.isPaused;
</script>

<div class="tab-content active">
	<h2 class="text-primary mb-6">タイマー</h2>
	
	<div class="text-center">
		<!-- タイマー表示 -->
		<div class="timer-display text-6xl font-bold text-primary font-mono mb-8">
			{displayTime}
		</div>
		
		<!-- 状態表示 -->
		<div class="timer-status mb-6">
			{#if $timer.seconds <= 0}
				<p class="text-warning text-lg">時間を設定してください</p>
			{:else if isRunning}
				<p class="text-success text-lg">タイマー実行中</p>
			{:else if isPaused}
				<p class="text-warning text-lg">一時停止中</p>
			{:else}
				<p class="text-info text-lg">準備完了</p>
			{/if}
		</div>
		
		<!-- コントロールボタン -->
		<div class="flex flex-center flex-gap mb-8">
			<button 
				class="btn btn-success btn-lg" 
				class:btn-warning={isRunning}
				disabled={$timer.seconds <= 0}
				on:click={isRunning ? pauseTimer : startTimer}
			>
				<i class="fas {isRunning ? 'fa-pause' : 'fa-play'}"></i>
				{isRunning ? '一時停止' : '開始'}
			</button>
			
			<button class="btn btn-danger btn-lg" on:click={resetTimer}>
				<i class="fas fa-stop"></i>
				リセット
			</button>
		</div>
		
		<!-- 時間設定ボタン -->
		<div class="mb-8">
			<button class="btn btn-primary btn-lg mb-4" on:click={openTimeModal}>
				<i class="fas fa-clock"></i>
				時間を設定
			</button>
		</div>

	</div>

	<!-- 時間設定モーダル -->
	{#if showTimeModal}
		<div class="modal-overlay" role="button" tabindex="0" on:click={() => showTimeModal = false} on:keydown={(e) => e.key === 'Escape' && (showTimeModal = false)}>
			<div class="modal" role="dialog" aria-modal="true" on:click|stopPropagation>
				<div class="modal-header">
					<h3>時間設定</h3>
					<button class="modal-close" on:click={() => showTimeModal = false}>
						<i class="fas fa-times"></i>
					</button>
				</div>
				
				<div class="modal-body">
					<div class="time-inputs">
						<div class="time-input-group">
							<label for="hours-input">時間</label>
							<input 
								id="hours-input"
								type="number" 
								bind:value={timeInput.hours} 
								min="0" 
								max="23"
								class="form-input"
							/>
						</div>
						<div class="time-input-group">
							<label for="minutes-input">分</label>
							<input 
								id="minutes-input"
								type="number" 
								bind:value={timeInput.minutes} 
								min="0" 
								max="59"
								class="form-input"
							/>
						</div>
						<div class="time-input-group">
							<label for="seconds-input">秒</label>
							<input 
								id="seconds-input"
								type="number" 
								bind:value={timeInput.seconds} 
								min="0" 
								max="59"
								class="form-input"
							/>
						</div>
					</div>
				</div>
				
				<div class="modal-footer">
					<button class="btn btn-secondary" on:click={() => showTimeModal = false}>
						キャンセル
					</button>
					<button class="btn btn-primary" on:click={setTime}>
						設定
					</button>
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.timer-display {
		text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
	}
	
	.timer-status p {
		font-weight: 600;
	}
	
	
	.time-inputs {
		display: flex;
		gap: 1rem;
		justify-content: center;
		align-items: end;
	}
	
	.time-input-group {
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	
	.time-input-group label {
		font-weight: 600;
		margin-bottom: 0.5rem;
		color: var(--text-color);
	}
	
	.time-input-group input {
		width: 80px;
		text-align: center;
		font-size: 1.2rem;
		font-weight: bold;
	}
	
	.btn-lg {
		padding: 0.75rem 1.5rem;
		font-size: 1.1rem;
		min-width: 120px;
	}
	
</style>