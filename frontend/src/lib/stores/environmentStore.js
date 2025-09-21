import { writable } from 'svelte/store';

export const environmentData = writable({
	temperature: 0,
	humidity: 0,
	co2: 0,
	loading: true,
	error: null
});

export const weatherData = writable({
	temperature: 0,
	humidity: 0,
	description: '',
	location: '高崎市',
	icon: 'fas fa-sun',
	loading: true,
	error: null
});

export const dateTime = writable({
	date: '',
	time: ''
});
