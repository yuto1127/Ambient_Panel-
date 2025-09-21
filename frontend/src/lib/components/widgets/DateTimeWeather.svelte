<script>
	import { onMount, onDestroy } from 'svelte';
	import { dateTime, weatherData } from '$lib/stores/environmentStore.js';
	import { api } from '$lib/utils/api.js';
	import { updateDateTime } from '$lib/utils/dateTime.js';

	let interval;

	onMount(async () => {
		// 日時の更新
		interval = setInterval(() => {
			dateTime.set(updateDateTime());
		}, 1000);

		// 天気データの取得
		try {
			const data = await api.getCurrentWeather();
			if (data.success) {
				weatherData.set({
					temperature: data.data.temperature,
					humidity: data.data.humidity,
					description: data.data.description,
					location: data.data.location,
					icon: getWeatherIcon(data.data.icon),
					loading: false,
					error: null
				});
			}
		} catch (error) {
			weatherData.update(state => ({
				...state,
				loading: false,
				error: error.message
			}));
		}
	});

	onDestroy(() => {
		if (interval) {
			clearInterval(interval);
		}
	});

	function getWeatherIcon(iconCode) {
		const iconMap = {
			'01d': 'fas fa-sun',
			'01n': 'fas fa-moon',
			'02d': 'fas fa-cloud-sun',
			'02n': 'fas fa-cloud-moon',
			'03d': 'fas fa-cloud',
			'03n': 'fas fa-cloud',
			'04d': 'fas fa-cloud',
			'04n': 'fas fa-cloud',
			'09d': 'fas fa-cloud-rain',
			'09n': 'fas fa-cloud-rain',
			'10d': 'fas fa-cloud-sun-rain',
			'10n': 'fas fa-cloud-moon-rain',
			'11d': 'fas fa-bolt',
			'11n': 'fas fa-bolt',
			'13d': 'fas fa-snowflake',
			'13n': 'fas fa-snowflake',
			'50d': 'fas fa-smog',
			'50n': 'fas fa-smog'
		};
		return iconMap[iconCode] || 'fas fa-sun';
	}
</script>

<div class="widget datetime-weather">
	<div class="datetime mb-6">
		<div class="date text-lg font-bold text-primary mb-2">
			{$dateTime.date}
		</div>
		<div class="time text-4xl font-bold text-primary font-mono">
			{$dateTime.time}
		</div>
	</div>
	
	<div class="weather">
		<div class="location text-sm text-muted mb-2">
			{$weatherData.location}
		</div>
		<div class="weather-info flex items-center gap-3">
			<div class="weather-icon text-2xl text-warning">
				<i class={$weatherData.icon}></i>
			</div>
			<div class="weather-details">
				<div class="temperature text-lg font-bold text-primary">
					{$weatherData.temperature}℃
				</div>
				<div class="humidity text-sm text-secondary">
					{$weatherData.humidity}%
				</div>
			</div>
		</div>
	</div>
</div>
