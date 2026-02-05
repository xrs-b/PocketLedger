<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
      <h1 class="text-2xl font-bold text-center mb-6">注册</h1>
      <form @submit.prevent="handleRegister">
        <div class="mb-4">
          <label class="block text-gray-700 mb-2">用户名</label>
          <input v-model="form.username" type="text" class="w-full border rounded px-3 py-2" required />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700 mb-2">密码</label>
          <input v-model="form.password" type="password" class="w-full border rounded px-3 py-2" required />
        </div>
        <div class="mb-6">
          <label class="block text-gray-700 mb-2">邀请码</label>
          <input v-model="form.invitation_code" type="text" class="w-full border rounded px-3 py-2" required />
        </div>
        <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
          注册
        </button>
      </form>
      <p class="mt-4 text-center">
        <router-link to="/login" class="text-blue-600">已有账号？去登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const form = ref({ username: '', password: '', invitation_code: '' })

const handleRegister = async () => {
  try {
    await axios.post('/api/v1/auth/register', form.value)
    router.push('/login')
  } catch (error) {
    alert('注册失败：' + (error.response?.data?.detail || '未知错误'))
  }
}
</script>
