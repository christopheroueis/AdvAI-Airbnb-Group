import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const forecastAPI = {
    // Forecast endpoints
    forecastVolume: (params) =>
        apiClient.post('/forecast/volume', params),

    forecastPrice: (params) =>
        apiClient.post('/forecast/price', params),

    forecastOccupancy: (params) =>
        apiClient.post('/forecast/occupancy', params),

    // Scenario endpoints
    getScenarios: () =>
        apiClient.get('/scenarios/scenarios'),

    getEvents: () =>
        apiClient.get('/scenarios/events'),

    simulateScenario: (params) =>
        apiClient.post('/scenarios/simulate', params),

    compareScenarios: (scenarioIds, horizon = 4) =>
        apiClient.post('/scenarios/compare', { scenario_ids: scenarioIds, horizon }),
};

export default apiClient;
