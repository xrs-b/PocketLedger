import client from './client'

export const auth = {
  async login(username, password) {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    
    const response = await client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    return response
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
