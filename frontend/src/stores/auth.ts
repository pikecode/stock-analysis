import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, subscriptionApi } from '@/api'
import type { User, LoginRequest } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const subscription = ref<any>(null)

  const isLoggedIn = computed(() => !!localStorage.getItem('access_token'))
  const isAdmin = computed(() => user.value?.roles.includes('admin') ?? false)
  const isCustomer = computed(() => user.value?.roles.includes('customer') ?? false)
  const roles = computed(() => user.value?.roles ?? [])
  const permissions = computed(() => user.value?.permissions ?? [])
  const hasValidSubscription = computed(() => subscription.value?.is_valid ?? false)
  const subscriptionDaysRemaining = computed(() => subscription.value?.days_remaining ?? 0)

  async function login(credentials: LoginRequest) {
    loading.value = true
    try {
      const res = await authApi.login(credentials)
      localStorage.setItem('access_token', res.access_token)
      localStorage.setItem('refresh_token', res.refresh_token)
      await fetchUser()
      return true
    } catch (error) {
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

  // 检查是否拥有指定的角色
  function hasRole(role: string): boolean {
    return roles.value.includes(role)
  }

  // 检查是否拥有指定的权限
  function hasPermission(permission: string): boolean {
    return permissions.value.includes(permission)
  }

  // 检查是否拥有所有指定的角色
  function hasAllRoles(roleList: string[]): boolean {
    return roleList.every(role => roles.value.includes(role))
  }

  // 检查是否拥有任意一个指定的角色
  function hasAnyRole(roleList: string[]): boolean {
    return roleList.some(role => roles.value.includes(role))
  }

  // 检查是否拥有所有指定的权限
  function hasAllPermissions(permissionList: string[]): boolean {
    return permissionList.every(perm => permissions.value.includes(perm))
  }

  // 检查是否拥有任意一个指定的权限
  function hasAnyPermission(permissionList: string[]): boolean {
    return permissionList.some(perm => permissions.value.includes(perm))
  }

  return {
    user,
    loading,
    subscription,
    isLoggedIn,
    isAdmin,
    isCustomer,
    roles,
    permissions,
    hasValidSubscription,
    subscriptionDaysRemaining,
    login,
    logout,
    fetchUser,
    fetchSubscription,
    hasRole,
    hasPermission,
    hasAllRoles,
    hasAnyRole,
    hasAllPermissions,
    hasAnyPermission,
  }
})
