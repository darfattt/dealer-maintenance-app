import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

// Create axios instance with environment-aware base URL
const getBaseURL = () => {
    // In production, use relative URL that will be proxied by nginx
    if (import.meta.env.PROD) {
        return '/api';
    }
    // In development, use the environment variable or fallback
    return  '/api'; //import.meta.env.VITE_API_BASE_URL ||
};

const api = axios.create({
    baseURL: getBaseURL(),
    timeout: 100000, // Increased timeout for production
    headers: {
        'Content-Type': 'application/json'
    },
    withCredentials: false
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const authStore = useAuthStore();
        if (authStore.token) {
            config.headers.Authorization = `Bearer ${authStore.token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const authStore = useAuthStore();
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const result = await authStore.refreshAccessToken();
                if (result.success) {
                    // Retry the original request with new token
                    originalRequest.headers.Authorization = `Bearer ${authStore.token}`;
                    return api(originalRequest);
                } else {
                    // Refresh failed, logout user
                    await authStore.logout();
                    window.location.href = '/auth/login';
                }
            } catch (refreshError) {
                // Refresh failed, logout user
                await authStore.logout();
                window.location.href = '/auth/login';
            }
        }

        return Promise.reject(error);
    }
);

export default api;
