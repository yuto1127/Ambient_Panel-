import { writable } from 'svelte/store';

export const environmentData = writable({
	temperature: 0,
	humidity: 0,
	co2: 0,
	loading: true,
	error: null
});

export const dateTime = writable({
	date: '',
	time: ''
});
