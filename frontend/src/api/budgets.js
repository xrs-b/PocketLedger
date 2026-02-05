import client from './client'

export const budgets = {
  // 获取预算列表（支持分页）
  async list(params = {}) {
    return await client.get('/budgets', { params })
  },

  // 获取预算详情
  async get(id) {
    return await client.get(`/budgets/${id}`)
  },

  // 创建预算
  async create(data) {
    return await client.post('/budgets', data)
  },

  // 更新预算
  async update(id, data) {
    return await client.put(`/budgets/${id}`, data)
  },

  // 删除预算
  async delete(id) {
    return await client.delete(`/budgets/${id}`)
  },

  // 获取超支提醒
  async getAlerts() {
    return await client.get('/budgets/alerts')
  }
}

export default budgets
