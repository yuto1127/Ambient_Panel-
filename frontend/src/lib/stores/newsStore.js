import { writable } from 'svelte/store';

export const newsData = writable({
	articles: [],
	loading: true,
	error: null
});

export const calendarData = writable({
	events: [],
	loading: true,
	error: null
});
