import axios from 'axios';
import { getToken } from './auth';
import { logout } from "./auth";

// configured Axios instance
const api = axios.create({
    // Default to localhost:8000
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

// requests to auto inject JWT
api.interceptors.request.use(
    (config) => {
        const token = getToken();
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            logout(); // clear token & redirect
        }
        return Promise.reject(error);
    }
);

export default api;