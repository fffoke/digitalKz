import axios from "axios";

// Бэк живёт на том же хосте, что открыт в браузере, но на порту 8000.
// На телефоне (по IP Mac) это будет http://192.168.x.x:8000/api,
// на компе — http://localhost:8000/api. Можно переопределить через VITE_API_URL.
const baseURL =
    import.meta.env.VITE_API_URL ||
    `${window.location.protocol}//${window.location.hostname}:8000/api`;

const api = axios.create({ baseURL });

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

export default api;