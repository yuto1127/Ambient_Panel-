<script>
	import { onMount, onDestroy } from 'svelte';
	import { dateTime } from '$lib/stores/environmentStore.js';
	import { updateDateTime } from '$lib/utils/dateTime.js';

	let interval;

	onMount(() => {
		// 日時の更新
		interval = setInterval(() => {
			dateTime.set(updateDateTime());
		}, 1000);
	});

	onDestroy(() => {
		if (interval) {
			clearInterval(interval);
		}
	});
</script>

<div class="widget datetime-weather">
	<div class="datetime">
		<div class="date text-lg font-bold text-primary mb-2">
			{$dateTime.date}
		</div>
		<div class="time text-4xl font-bold text-primary font-mono">
			{$dateTime.time}
		</div>
	</div>
</div>
