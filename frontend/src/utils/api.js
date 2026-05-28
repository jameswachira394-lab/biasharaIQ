import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach token automatically
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('biasharaiq_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('biasharaiq_token')
      localStorage.removeItem('biasharaiq_user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// Auth
export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
}

// Transactions
export const transactionsApi = {
  list: (params) => api.get('/transactions/', { params }),
  create: (data) => api.post('/transactions/', data),
  update: (id, data) => api.put(`/transactions/${id}`, data),
  delete: (id) => api.delete(`/transactions/${id}`),
  get: (id) => api.get(`/transactions/${id}`),
}

// Dashboard
export const dashboardApi = {
  get: () => api.get('/dashboard/'),
}

// Insights
export const insightsApi = {
  get: () => api.get('/insights/'),
  history: (limit = 20) => api.get('/insights/history', { params: { limit } }),
}

// AI Agent
export const aiApi = {
  chat: (message, history = []) =>
    api.post('/ai/chat', { message, history }),
}

// Reports
export const reportsApi = {
  monthly: () => api.get('/reports/monthly'),
  weeklyTrend: (weeks = 8) => api.get('/reports/weekly-trend', { params: { weeks } }),
}

// Categories
export const categoriesApi = {
  list: (type) => api.get('/categories/', { params: type ? { type } : {} }),
  create: (data) => api.post('/categories/', data),
  delete: (id) => api.delete(`/categories/${id}`),
}

// Profile
export const profileApi = {
  get: () => api.get('/profile/'),
  update: (data) => api.put('/profile/', data),
}

// Subscription
export const subscriptionApi = {
  status: () => api.get('/subscription/status'),
  plans: () => api.get('/subscription/plans'),
}

// Payments
export const paymentApi = {
  initiate: (data) => api.post('/payments/initiate', data),
  status: (checkoutId) => api.get(`/payments/status/${checkoutId}`),
}

export default api
