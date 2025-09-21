import { writable } from 'svelte/store';

export const spotifyStatus = writable({
	isPlaying: false,
	track: {
		name: '--',
		artist: '--',
		album: '--',
		image_url: '/static/images/default-album.png',
		duration_ms: 0,
		progress_ms: 0
	},
	device: {
		name: 'Ambient Panel',
		volume_percent: 50
	},
	loading: true,
	error: null
});

export const playlists = writable({
	items: [],
	loading: true,
	error: null
});
