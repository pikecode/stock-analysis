import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, subscriptionApi } from '@/api'
import type { User, LoginRequest } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const subscription = ref<any>(null)

  const isLoggedIn = computed(() => !!localStorage.getItem('access_token'))
  const isAdmin = computed(() => user.value?.role === 'ADMIN')
  const isVip = computed(() => user.value?.role === 'VIP')
  const isCustomer = computed(() => user.value?.role === 'VIP' || user.value?.role === 'NORMAL')
  const role = computed(() => user.value?.role ?? null)
  const hasValidSubscription = computed(() => subscription.value?.is_valid ?? false)
  const subscriptionDaysRemaining = computed(() => subscription.value?.days_remaining ?? 0)

  async function login(credentials: LoginRequest) {
    console.log('🟠 [Auth Store] login() 被调用，凭证:', { username: credentials.username })
    loading.value = true
    try {
      console.log('🟠 [Auth Store] 正在调用 authApi.login()...')
      const res = await authApi.login(credentials)
      console.log('🟠 [Auth Store] authApi.login() 返回:', res)

      localStorage.setItem('access_token', res.access_token)
      localStorage.setItem('refresh_token', res.refresh_token)
      console.log('🟠 [Auth Store] Token已保存到localStorage')

      await fetchUser()
      console.log('🟠 [Auth Store] 用户信息已加载:', user.value)
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

  async function logout() {
    try {
      await authApi.logout()
    } catch {
      // Ignore logout errors
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      user.value = null
    }
  }

  async function fetchUser() {
    if (!localStorage.getItem('access_token')) return
    try {
      user.value = await authApi.getMe()
      // Also fetch subscription status
      await fetchSubscription()
    } catch {
      user.value = null
    }
  }

  async function fetchSubscription() {
    if (!localStorage.getItem('access_token')) return
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
    loading,
    subscription,
    isLoggedIn,
    isAdmin,
    isVip,
    isCustomer,
    role,
    hasValidSubscription,
    subscriptionDaysRemaining,
    login,
    logout,
    fetchUser,
    fetchSubscription,
    hasRole,
    hasAnyRole,
  }
})
