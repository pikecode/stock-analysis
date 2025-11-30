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
    // 根据请求路径选择正确的 token（管理员还是客户端）
    let token: string | null = null
    if (config.url?.includes('/admin')) {
      token = localStorage.getItem('admin_access_token')
    } else {
      token = localStorage.getItem('client_access_token')
    }

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
        case 400:
          // 400 Bad Request - 通常是验证失败或登录失败
          ElMessage.error(data.detail || data.message || '请求参数错误')
          break

        case 401:
          // Special handling for login failures - show error without redirect
          if (error.config?.url?.includes('/auth/login')) {
            ElMessage.error(data.detail || '用户名或密码错误')
            break
          }

          // For other 401 errors, try to refresh token
          const isAdminPath = error.config?.url?.includes('/admin')
          const tokenKey = isAdminPath ? 'admin_refresh_token' : 'client_refresh_token'
          const accessTokenKey = isAdminPath ? 'admin_access_token' : 'client_access_token'
          const refreshToken = localStorage.getItem(tokenKey)

          if (refreshToken && !error.config?.url?.includes('/auth/')) {
            try {
              const res = await axios.post(`${baseURL}/auth/refresh`, {
                refresh_token: refreshToken,
              })
              const { access_token, refresh_token } = res.data
              localStorage.setItem(accessTokenKey, access_token)
              localStorage.setItem(tokenKey, refresh_token)

              // Retry original request
              if (error.config) {
                error.config.headers.Authorization = `Bearer ${access_token}`
                return request(error.config)
              }
            } catch {
              // Refresh failed, logout
              localStorage.removeItem(accessTokenKey)
              localStorage.removeItem(tokenKey)
              ElMessage.error('登录已过期，请重新登录')
              window.location.href = isAdminPath ? '/admin-login' : '/login'
            }
          } else {
            localStorage.removeItem(accessTokenKey)
            localStorage.removeItem(tokenKey)
            ElMessage.error('登录已过期，请重新登录')
            window.location.href = isAdminPath ? '/admin-login' : '/login'
          }
          break

        case 403:
          ElMessage.error(data.detail || '您没有权限访问此功能')
          break

        case 404:
          ElMessage.error(data.detail || 'Resource not found')
          break

        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break

        default:
          ElMessage.error(data.detail || data.message || 'Request failed')
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      ElMessage.error('网络连接失败，请检查网络设置')
    } else {
      // 请求配置出错
      ElMessage.error('请求出错，请稍后重试')
    }

    return Promise.reject(error)
  }
)

export default request
