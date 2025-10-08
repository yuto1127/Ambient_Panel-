import { writable } from 'svelte/store';

export const currentTab = writable('spotify');

export const tabs = [
	{ id: 'calendar', label: 'Calendar', icon: 'fas fa-calendar' },
	{ id: 'spotify', label: 'Spotify', icon: 'fab fa-spotify' },
	{ id: 'timer', label: 'Timer', icon: 'fas fa-clock' },
	{ id: 'pdtimer', label: 'PDTimer', icon: 'fas fa-stopwatch' },
	{ id: 'news', label: 'News', icon: 'fas fa-newspaper' }
];
