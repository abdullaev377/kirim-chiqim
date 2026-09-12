import axios from 'axios'

const client = axios.create({ baseURL: '/' })
let refreshing = null

export function saveTokens(data) {
  const tokens = data?.token || data || {}
  if (tokens.access) localStorage.setItem('access', tokens.access)
  if (tokens.refresh) localStorage.setItem('refresh', tokens.refresh)
}

export function clearTokens() {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  localStorage.removeItem('ledgerly_profile')
}

export function getApiError(error) {
  if (!error.response) return 'Network error. Check that the API is running.'
  const data = error.response.data || {}
  const flatten = value => typeof value === 'object' && value !== null ? Object.values(value).flatMap(flatten) : [value]
  return data.msg || data.detail || Object.values(data).flatMap(flatten).filter(Boolean).join(' ') || `Request failed (${error.response.status})`
}

client.interceptors.request.use(config => {
  const token = localStorage.getItem('access')
  const isRefreshRequest = config.url?.includes('/auth/token-refresh')
  if (token && !isRefreshRequest) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(response => response, async error => {
  const original = error.config
  if (error.response?.status !== 401 || original?._retry || original?.url?.includes('/auth/token-refresh')) throw error
  const refresh = localStorage.getItem('refresh')
  if (!refresh) { clearTokens(); window.dispatchEvent(new Event('ledgerly:logout')); throw error }
  original._retry = true
  try {
    refreshing ||= axios.post('/auth/token-refresh', { refresh })
    const response = await refreshing
    refreshing = null
    saveTokens(response.data)
    original.headers.Authorization = `Bearer ${response.data.access}`
    return client(original)
  } catch (refreshError) {
    refreshing = null
    clearTokens()
    window.dispatchEvent(new Event('ledgerly:logout'))
    throw refreshError
  }
})

export default client