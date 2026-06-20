import axios from 'axios'

// Бэк на том же хосте, порт 8000. Логин — /auth/login, админ-ручки — /admin/*.
const baseURL =
  import.meta.env.VITE_API_URL ||
  `${window.location.protocol}//${window.location.hostname}:8000/api`

const api = axios.create({ baseURL })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default api
