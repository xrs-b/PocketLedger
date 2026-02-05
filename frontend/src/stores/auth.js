import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import client from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  
  // Actions
  async function login(username, password) {
    const response = await client.post('/auth/login', { username, password })
    token.value = response.access_token
    localStorage.setItem('token', response.access_token)
    return response
  }
  
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }
  
  return {
    token,
    user,
    isLoggedIn,
    login,
    logout
  }
})
