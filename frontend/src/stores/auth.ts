import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, subscriptionApi } from '@/api'
import type { User, LoginRequest } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // 双token独立存储
  const adminUser = ref<User | null>(null)
  const clientUser = ref<User | null>(null)
  const loading = ref(false)
  const subscription = ref<any>(null)

  // 当前活跃用户（根据已登录的身份确定）
  const user = computed(() => adminUser.value || clientUser.value)

  const isAdminLoggedIn = computed(() => !!localStorage.getItem('admin_access_token'))
  const isClientLoggedIn = computed(() => !!localStorage.getItem('client_access_token'))
  const isLoggedIn = computed(() => isAdminLoggedIn.value || isClientLoggedIn.value)

  const isAdmin = computed(() => adminUser.value?.role === 'ADMIN')
  const isVip = computed(() => clientUser.value?.role === 'VIP')
  const isCustomer = computed(() => clientUser.value?.role === 'VIP' || clientUser.value?.role === 'NORMAL')
  const role = computed(() => user.value?.role ?? null)
  const hasValidSubscription = computed(() => subscription.value?.is_valid ?? false)
  const subscriptionDaysRemaining = computed(() => subscription.value?.days_remaining ?? 0)

  async function login(credentials: LoginRequest, loginType: 'admin' | 'client' = 'client') {
    console.log('🟠 [Auth Store] login() 被调用，凭证:', { username: credentials.username, loginType })
    loading.value = true
    try {
      console.log('🟠 [Auth Store] 正在调用 authApi.login()...')
      const res = await authApi.login(credentials)
      console.log('🟠 [Auth Store] authApi.login() 返回:', res)

      // 根据登录类型分别存储 token
      if (loginType === 'admin') {
        localStorage.setItem('admin_access_token', res.access_token)
        localStorage.setItem('admin_refresh_token', res.refresh_token)
        console.log('🟠 [Auth Store] Admin Token已保存到localStorage')
        try {
          await fetchAdminUser()
          console.log('🟠 [Auth Store] Admin 用户信息已加载')
        } catch (fetchError) {
          console.error('🟠 [Auth Store] 获取 Admin 用户信息失败:', fetchError)
          return false
        }
      } else {
        localStorage.setItem('client_access_token', res.access_token)
        localStorage.setItem('client_refresh_token', res.refresh_token)
        console.log('🟠 [Auth Store] Client Token已保存到localStorage')
        try {
          await fetchClientUser()
          console.log('🟠 [Auth Store] Client 用户信息已加载')
        } catch (fetchError) {
          console.error('🟠 [Auth Store] 获取 Client 用户信息失败:', fetchError)
          return false
        }
      }

      console.log('🟠 [Auth Store] 登录完全成功，用户信息:', user.value)
      return true
    } catch (error: any) {
      console.error('🟠 [Auth Store] 登录异常:', error)
      console.error('🟠 [Auth Store] 错误详情:', {
        message: error?.message,
        response: error?.response?.data,
        status: error?.response?.status,
      })
      return false
    } finally {
      loading.value = false
    }
  }

  async function logout(logoutType: 'admin' | 'client' | 'all' = 'all') {
    try {
      await authApi.logout()
    } catch {
      // Ignore logout errors
    } finally {
      if (logoutType === 'admin' || logoutType === 'all') {
        localStorage.removeItem('admin_access_token')
        localStorage.removeItem('admin_refresh_token')
        adminUser.value = null
      }

      if (logoutType === 'client' || logoutType === 'all') {
        localStorage.removeItem('client_access_token')
        localStorage.removeItem('client_refresh_token')
        clientUser.value = null
      }
    }
  }

  async function fetchAdminUser() {
    const token = localStorage.getItem('admin_access_token')
    if (!token) {
      console.warn('[Auth Store] fetchAdminUser: 没有 admin_access_token')
      adminUser.value = null
      return
    }
    try {
      console.log('[Auth Store] 正在获取 admin 用户信息...')
      // 使用 admin token 调用 getMe
      // 创建一个临时请求实例，明确使用 admin token
      const response = await fetch('/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      adminUser.value = await response.json()
      console.log('[Auth Store] admin 用户信息获取成功:', adminUser.value)
    } catch (error) {
      console.error('[Auth Store] 获取 admin 用户信息失败:', error)
      adminUser.value = null
      localStorage.removeItem('admin_access_token')
      localStorage.removeItem('admin_refresh_token')
      throw error
    }
  }

  async function fetchClientUser() {
    const token = localStorage.getItem('client_access_token')
    if (!token) {
      console.warn('[Auth Store] fetchClientUser: 没有 client_access_token')
      clientUser.value = null
      return
    }
    try {
      console.log('[Auth Store] 正在获取 client 用户信息...')
      // 使用 client token 调用 getMe
      // 创建一个临时请求实例，明确使用 client token
      const response = await fetch('/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      clientUser.value = await response.json()
      console.log('[Auth Store] client 用户信息获取成功:', clientUser.value)
      // Also fetch subscription status
      await fetchSubscription()
    } catch (error) {
      console.error('[Auth Store] 获取 client 用户信息失败:', error)
      clientUser.value = null
      localStorage.removeItem('client_access_token')
      localStorage.removeItem('client_refresh_token')
      throw error
    }
  }

  async function fetchUser() {
    // 兼容旧代码：先尝试获取 admin user，再尝试获取 client user
    const adminToken = localStorage.getItem('admin_access_token')
    const clientToken = localStorage.getItem('client_access_token')

    if (adminToken) {
      await fetchAdminUser()
    }
    if (clientToken) {
      await fetchClientUser()
    }
  }

  async function fetchSubscription() {
    if (!localStorage.getItem('client_access_token')) return
    try {
      subscription.value = await subscriptionApi.checkValidity()
    } catch {
      subscription.value = null
    }
  }

  // 检查是否拥有指定的角色 (不区分大小写)
  function hasRole(requiredRole: string): boolean {
    return role.value?.toUpperCase() === requiredRole.toUpperCase()
  }

  // 检查是否拥有任意一个指定的角色 (不区分大小写)
  function hasAnyRole(roleList: string[]): boolean {
    const currentRole = role.value?.toUpperCase() ?? ''
    return roleList.map(r => r.toUpperCase()).includes(currentRole)
  }

  return {
    user,
    adminUser,
    clientUser,
    loading,
    subscription,
    isLoggedIn,
    isAdminLoggedIn,
    isClientLoggedIn,
    isAdmin,
    isVip,
    isCustomer,
    role,
    hasValidSubscription,
    subscriptionDaysRemaining,
    login,
    logout,
    fetchUser,
    fetchAdminUser,
    fetchClientUser,
    fetchSubscription,
    hasRole,
    hasAnyRole,
  }
})
