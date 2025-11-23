import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'
import type { User, LoginRequest } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!localStorage.getItem('access_token'))
  const isAdmin = computed(() => user.value?.roles.includes('admin') ?? false)

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
    } catch {
      user.value = null
    }
  }

  return {
    user,
    loading,
    isLoggedIn,
    isAdmin,
    login,
    logout,
    fetchUser,
  }
})
