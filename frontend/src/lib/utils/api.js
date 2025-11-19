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
			
			// レスポンスが空の場合（204 No Content）を処理
			if (response.status === 204 || response.headers.get('content-length') === '0') {
				return { success: true, data: {} };
			}
			
			// Content-TypeをチェックしてJSONかどうか判定
			const contentType = response.headers.get('content-type');
			if (contentType && contentType.includes('application/json')) {
				const jsonData = await response.json();
				console.log(`API response for ${endpoint}:`, jsonData);
				return jsonData;
			} else {
				// JSONでない場合や空のレスポンスの場合
				const text = await response.text();
				console.log(`Non-JSON response for ${endpoint}:`, text);
				if (!text.trim()) {
					return { success: true, data: {} };
				}
				return { success: true, data: text };
			}
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

	async playTrack(trackUri = null) {
		const url = trackUri ? `/spotify/play?track_uri=${encodeURIComponent(trackUri)}` : '/spotify/play';
		return this.request(url, { method: 'POST' });
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
}

export const api = new ApiClient();
