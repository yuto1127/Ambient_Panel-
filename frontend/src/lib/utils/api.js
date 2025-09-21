const API_BASE = '/api';

class ApiClient {
	async request(endpoint, options = {}) {
		const url = `${API_BASE}${endpoint}`;
		const config = {
			headers: {
				'Content-Type': 'application/json',
				...options.headers
			},
			...options
		};

		try {
			const response = await fetch(url, config);
			
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			
			return await response.json();
		} catch (error) {
			console.error(`API request failed for ${endpoint}:`, error);
			throw error;
		}
	}

	// Environment API
	async getEnvironmentData() {
		return this.request('/environment/');
	}

	async getSensorStatus() {
		return this.request('/environment/status');
	}

	// Weather API
	async getCurrentWeather() {
		return this.request('/weather/current');
	}

	async getWeatherForecast() {
		return this.request('/weather/forecast');
	}

	// Spotify API
	async getSpotifyStatus() {
		return this.request('/spotify/status');
	}

	async getCurrentPlayback() {
		return this.request('/spotify/current');
	}

	async getPlaylists() {
		return this.request('/spotify/playlists');
	}

	async playTrack(trackId = null) {
		return this.request('/spotify/play', {
			method: 'POST',
			body: JSON.stringify({ track_id: trackId })
		});
	}

	async pausePlayback() {
		return this.request('/spotify/pause', { method: 'POST' });
	}

	async nextTrack() {
		return this.request('/spotify/next', { method: 'POST' });
	}

	async previousTrack() {
		return this.request('/spotify/previous', { method: 'POST' });
	}

	// Calendar API
	async getCalendarEvents() {
		return this.request('/calendar/events');
	}

	async getTodayEvents() {
		return this.request('/calendar/today');
	}

	async getMonthEvents(year, month) {
		return this.request(`/calendar/month/${year}/${month}`);
	}

	async getDayEvents(year, month, day) {
		return this.request(`/calendar/day/${year}/${month}/${day}`);
	}

	// News API
	async getNewsHeadlines() {
		return this.request('/news/headlines');
	}

	async getNewsByCategory(category) {
		return this.request(`/news/category/${category}`);
	}
}

export const api = new ApiClient();
