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
    console.log(`[API请求] ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`, {
      data: config.data,
    })

    // 根据请求路径选择正确的 token（管理员还是客户端）
    let token: string | null = null
    if (config.url?.includes('/admin')) {
      token = localStorage.getItem('admin_access_token')
      console.log('[API请求] 使用 admin_access_token')
    } else {
      token = localStorage.getItem('client_access_token')
      console.log('[API请求] 使用 client_access_token')
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('[API请求] 配置错误:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error: AxiosError) => {
    console.error('API 请求错误:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    })

    if (error.response) {
      const status = error.response.status
      const data = error.response.data as any

      switch (status) {
        case 400:
          // 400 Bad Request - 通常是验证失败或登录失败
          ElMessage.error(data.detail || data.message || '请求参数错误')
          break

        case 401:
          // 根据请求路径选择要刷新的 token
          const isAdminPath = error.config?.url?.includes('/admin')
          const tokenKey = isAdminPath ? 'admin_refresh_token' : 'client_refresh_token'
          const accessTokenKey = isAdminPath ? 'admin_access_token' : 'client_access_token'
          const refreshToken = localStorage.getItem(tokenKey)

          if (refreshToken && !error.config?.url?.includes('/auth/')) {
            try {
              console.log(`[API] 尝试刷新 ${isAdminPath ? 'admin' : 'client'} token...`)
              const res = await axios.post(`${baseURL}/auth/refresh`, {
                refresh_token: refreshToken,
              })
              const { access_token, refresh_token } = res.data
              localStorage.setItem(accessTokenKey, access_token)
              localStorage.setItem(tokenKey, refresh_token)
              console.log(`[API] ${isAdminPath ? 'admin' : 'client'} token 刷新成功`)

              // Retry original request
              if (error.config) {
                error.config.headers.Authorization = `Bearer ${access_token}`
                return request(error.config)
              }
            } catch {
              // Refresh failed, logout
              console.error(`[API] ${isAdminPath ? 'admin' : 'client'} token 刷新失败`)
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
      console.error('网络请求失败 - 没有收到响应:', error.request)
      ElMessage.error('网络连接失败，请检查网络设置')
    } else {
      // 请求配置出错
      console.error('请求配置错误:', error.message)
      ElMessage.error('请求出错，请稍后重试')
    }

    return Promise.reject(error)
  }
)

export default request
