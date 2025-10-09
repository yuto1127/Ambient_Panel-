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
		<div class="timer-display font-bold text-primary font-mono mb-8">
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
							<label>時間</label>
							<div class="input-controls">
								<button 
									class="btn btn-sm btn-secondary"
									on:click={() => timeInput.hours = Math.max(0, timeInput.hours - 1)}
								>
									<i class="fas fa-minus"></i>
								</button>
								<input 
									type="text" 
									value={timeInput.hours} 
									readonly
									class="form-input"
								/>
								<button 
									class="btn btn-sm btn-secondary"
									on:click={() => timeInput.hours = Math.min(23, timeInput.hours + 1)}
								>
									<i class="fas fa-plus"></i>
								</button>
							</div>
						</div>
						<div class="time-input-group">
							<label>分</label>
							<div class="input-controls">
								<button 
									class="btn btn-sm btn-secondary"
									on:click={() => timeInput.minutes = Math.max(0, timeInput.minutes - 1)}
								>
									<i class="fas fa-minus"></i>
								</button>
								<input 
									type="text" 
									value={timeInput.minutes} 
									readonly
									class="form-input"
								/>
								<button 
									class="btn btn-sm btn-secondary"
									on:click={() => timeInput.minutes = Math.min(59, timeInput.minutes + 1)}
								>
									<i class="fas fa-plus"></i>
								</button>
							</div>
						</div>
						<div class="time-input-group">
							<label>秒</label>
							<div class="input-controls">
								<button 
									class="btn btn-sm btn-secondary"
									on:click={() => timeInput.seconds = Math.max(0, timeInput.seconds - 1)}
								>
									<i class="fas fa-minus"></i>
								</button>
								<input 
									type="text" 
									value={timeInput.seconds} 
									readonly
									class="form-input"
								/>
								<button 
									class="btn btn-sm btn-secondary"
									on:click={() => timeInput.seconds = Math.min(59, timeInput.seconds + 1)}
								>
									<i class="fas fa-plus"></i>
								</button>
							</div>
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
	
	.input-controls {
		display: flex;
		gap: 0.5rem;
		align-items: center;
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
	
</style>