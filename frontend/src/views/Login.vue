<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
      <h1 class="text-2xl font-bold text-center mb-6">登录</h1>
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-gray-700 mb-2">用户名</label>
          <input v-model="form.username" type="text" class="w-full border rounded px-3 py-2" required />
        </div>
        <div class="mb-6">
          <label class="block text-gray-700 mb-2">密码</label>
          <input v-model="form.password" type="password" class="w-full border rounded px-3 py-2" required />
        </div>
        <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
          登录
        </button>
      </form>
      <p class="mt-4 text-center">
        <router-link to="/register" class="text-blue-600">没有账号？去注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const form = ref({ username: '', password: '' })

const handleLogin = async () => {
  try {
    const { data } = await axios.post('/api/v1/auth/login', form.value)
    localStorage.setItem('token', data.access_token)
    router.push('/')
  } catch (error) {
    alert('登录失败')
  }
}
</script>
