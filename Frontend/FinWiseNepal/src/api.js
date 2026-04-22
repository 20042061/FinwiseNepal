/**
 * FinWise Nepal — Centralized API Service
 * ----------------------------------------
 * Axios instance with JWT auth, token refresh, and all API endpoints
 * for authentication, NEPSE, planner, portfolio, reports, and admin.
 */

import axios from 'axios';

const API_URL = 'http://127.0.0.1:8001/api';

const api = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Auto-refresh token on 401 responses
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                const refreshToken = localStorage.getItem('refresh_token');
                const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
                    refresh: refreshToken,
                });
                localStorage.setItem('access_token', response.data.access);
                originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
                return api(originalRequest);
            } catch (refreshError) {
                localStorage.clear();
                window.location.href = '/';
                return Promise.reject(refreshError);
            }
        }
        return Promise.reject(error);
    }
);

// ========== Authentication ==========
export const authAPI = {
    register: (userData) => api.post('/auth/register/', userData),
    login: (credentials) => api.post('/auth/login/', credentials),
    getCurrentUser: () => api.get('/auth/me/'),
};

// ========== Chat ==========
export const chatAPI = {
    getSessions: () => api.get('/chat/sessions/'),
    createSession: () => api.post('/chat/sessions/', {}),
    getSession: (id) => api.get(`/chat/sessions/${id}/`),
    sendMessage: (sessionId, message) =>
        api.post(`/chat/sessions/${sessionId}/send/`, { message }),
    deleteSession: (id) => api.delete(`/chat/sessions/${id}/`),
};

// ========== Profile ==========
export const profileAPI = {
    getProfile: () => api.get('/profile/'),
    updateProfile: (data) => api.put('/profile/', data),
};

// ========== Education ==========
export const educationAPI = {
    getResources: (params) => api.get('/education/resources/', { params }),
    getResource: (id) => api.get(`/education/resources/${id}/`),
};

// ========== Dashboard ==========
export const dashboardAPI = {
    getStats: () => api.get('/dashboard/stats/'),
};

// ========== NEPSE Analytics ==========
export const nepseAPI = {
    getSummary: () => api.get('/nepse/summary/'),
    getHistorical: (params) => api.get('/nepse/historical/', { params }),
    getAnalytics: (params) => api.get('/nepse/analytics/', { params }),
    getVolume: (params) => api.get('/nepse/volume/', { params }),
};

// ========== Investment Planner ==========
export const plannerAPI = {
    getGoals: (params) => api.get('/planner/goals/', { params }),
    createGoal: (data) => api.post('/planner/goals/', data),
    getGoal: (id) => api.get(`/planner/goals/${id}/`),
    updateGoal: (id, data) => api.put(`/planner/goals/${id}/`, data),
    deleteGoal: (id) => api.delete(`/planner/goals/${id}/`),
    addContribution: (goalId, data) => api.post(`/planner/goals/${goalId}/contribute/`, data),
    getProjection: (goalId) => api.get(`/planner/goals/${goalId}/projection/`),
    getSummary: () => api.get('/planner/goals/summary/'),
};

// ========== Portfolio & Rebalancing ==========
export const portfolioAPI = {
    getPortfolios: () => api.get('/portfolio/'),
    createPortfolio: (data) => api.post('/portfolio/', data),
    getPortfolio: (id) => api.get(`/portfolio/${id}/`),
    updatePortfolio: (id, data) => api.put(`/portfolio/${id}/`, data),
    deletePortfolio: (id) => api.delete(`/portfolio/${id}/`),
    addAsset: (portfolioId, data) => api.post(`/portfolio/${portfolioId}/assets/`, data),
    updateAsset: (portfolioId, assetId, data) =>
        api.put(`/portfolio/${portfolioId}/assets/${assetId}/`, data),
    deleteAsset: (portfolioId, assetId) =>
        api.delete(`/portfolio/${portfolioId}/assets/${assetId}/`),
    rebalance: (portfolioId) => api.post(`/portfolio/${portfolioId}/rebalance/`),
    getRebalancingHistory: (portfolioId) =>
        api.get(`/portfolio/${portfolioId}/rebalancing-history/`),
};

// ========== Health Scores ==========
export const healthAPI = {
    computeScore: () => api.get('/portfolio/health-score/'),
    getHistory: () => api.get('/portfolio/health-score/history/'),
};

// ========== Reports ==========
export const reportsAPI = {
    getReports: (params) => api.get('/reports/', { params }),
    getReport: (id) => api.get(`/reports/${id}/`),
    generateReport: (data) => api.post('/reports/generate/', data),
    deleteReport: (id) => api.delete(`/reports/${id}/delete/`),
};

export default api;
