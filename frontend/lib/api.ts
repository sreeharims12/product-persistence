import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token from localStorage on every request
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 Unauthorized globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/auth';
      }
    }
    return Promise.reject(error);
  }
);

// ─── Auth ────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data: { email: string; password: string; full_name: string; phone?: string }) =>
    api.post('/api/auth/register', data),
  login: (email: string, password: string) =>
    api.post('/api/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  me: () => api.get('/api/auth/me'),
};

// ─── Products ────────────────────────────────────────────────────────────────
export const productsApi = {
  search: (q: string) => api.get('/api/products/search', { params: { q } }),
};

// ─── Monitoring ──────────────────────────────────────────────────────────────
export const monitoringApi = {
  list: () => api.get('/api/monitoring'),
  create: (data: { product_name: string; interval_minutes: number; notify_email: boolean; notify_sms: boolean }) =>
    api.post('/api/monitoring', data),
  get: (id: string) => api.get(`/api/monitoring/${id}`),
  update: (id: string, data: Partial<{ interval_minutes: number; is_active: boolean; notify_email: boolean; notify_sms: boolean }>) =>
    api.patch(`/api/monitoring/${id}`, data),
  remove: (id: string) => api.delete(`/api/monitoring/${id}`),
  snapshots: (id: string) => api.get(`/api/monitoring/${id}/snapshots`),
  priceHistory: (id: string) => api.get(`/api/monitoring/${id}/price-history`),
};

// ─── Notifications ───────────────────────────────────────────────────────────
export const notificationsApi = {
  list: () => api.get('/api/notifications'),
};

export default api;
