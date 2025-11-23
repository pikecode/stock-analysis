import axios, { AxiosError, AxiosInstance } from 'axios'
import { ElMessage } from 'element-plus'

const baseURL = '/api/v1'

const request: AxiosInstance = axios.create({
  baseURL,
  timeout: 30000,
})

// Request interceptor
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error: AxiosError) => {
    if (error.response) {
      const status = error.response.status
      const data = error.response.data as any

      switch (status) {
        case 401:
          // Try refresh token
          const refreshToken = localStorage.getItem('refresh_token')
          if (refreshToken && !error.config?.url?.includes('/auth/')) {
            try {
              const res = await axios.post(`${baseURL}/auth/refresh`, {
                refresh_token: refreshToken,
              })
              const { access_token, refresh_token } = res.data
              localStorage.setItem('access_token', access_token)
              localStorage.setItem('refresh_token', refresh_token)

              // Retry original request
              if (error.config) {
                error.config.headers.Authorization = `Bearer ${access_token}`
                return request(error.config)
              }
            } catch {
              // Refresh failed, logout
              localStorage.removeItem('access_token')
              localStorage.removeItem('refresh_token')
              window.location.href = '/login'
            }
          } else {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/login'
          }
          break

        case 403:
          ElMessage.error('Permission denied')
          break

        case 404:
          ElMessage.error(data.detail || 'Resource not found')
          break

        case 500:
          ElMessage.error('Server error')
          break

        default:
          ElMessage.error(data.detail || data.message || 'Request failed')
      }
    } else {
      ElMessage.error('Network error')
    }

    return Promise.reject(error)
  }
)

export default request
