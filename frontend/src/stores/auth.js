import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import auth from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const profile = ref(null)
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isAuthenticated = computed(() => !!token.value)
  
  // Actions
  async function login(email, password) {
    const response = await auth.login(email, password)
    token.value = response.access_token
    localStorage.setItem('token', response.access_token)
    await fetchProfile()
    return response
  }
  
  async function register(data) {
    const response = await auth.register(data)
    return response
  }
  
  function logout() {
    token.value = ''
    user.value = null
    profile.value = null
    localStorage.removeItem('token')
  }
  
  async function fetchProfile() {
    try {
      const response = await auth.getProfile()
      profile.value = response
      user.value = response
    } catch (error) {
      // 401 时清除状态
      if (error.response?.status === 401) {
        logout()
      }
    }
  }
  
  async function updateProfile(data) {
    const response = await auth.updateProfile(data)
    profile.value = response
    user.value = response
    return response
  }
  
  return {
    token,
    user,
    profile,
    isLoggedIn,
    isAuthenticated,
    login,
    register,
    logout,
    fetchProfile,
    updateProfile
  }
})
