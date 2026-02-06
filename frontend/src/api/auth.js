import client from './client'

export const auth = {
  async login(email, password) {
    // 发送 JSON 格式
    return await client.post('/auth/login', {
      email: email,
      password: password
    })
  },

  async register(data) {
    return await client.post('/auth/register', data)
  },

  async logout() {
    return await client.post('/auth/logout')
  },

  async getProfile() {
    return await client.get('/auth/me')
  },

  async refreshToken() {
    return await client.post('/auth/refresh')
  }
}

export default auth
