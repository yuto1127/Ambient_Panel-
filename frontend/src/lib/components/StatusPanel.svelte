<script>
	import DateTimeWeather from './widgets/DateTimeWeather.svelte';
	import EnvironmentWidget from './widgets/EnvironmentWidget.svelte';
	import TodaySchedule from './widgets/TodaySchedule.svelte';
	import SpotifyNowPlaying from './widgets/SpotifyNowPlaying.svelte';
</script>

<div class="status-panel">
	<DateTimeWeather />
	<EnvironmentWidget />
	<SpotifyNowPlaying />
	<TodaySchedule />
</div>
