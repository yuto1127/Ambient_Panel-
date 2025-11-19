import { writable } from 'svelte/store';

export const calendarData = writable({
	events: [],
	loading: true,
	error: null
});
