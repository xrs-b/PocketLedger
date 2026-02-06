import client from './client'

export const records = {
  // 获取记录列表（支持筛选）
  async list(params = {}) {
    return await client.get('/records', { params })
  },

  // 获取记录详情
  async get(id) {
    return await client.get(`/records/${id}`)
  },

  // 创建记录
  async create(data) {
    return await client.post('/records', data)
  },

  // 更新记录
  async update(id, data) {
    return await client.put(`/records/${id}`, data)
  },

  // 删除记录
  async delete(id) {
    return await client.delete(`/records/${id}`)
  },

  // 关联到项目
  async addToProject(recordId, projectId) {
    return await client.post(`/records/${recordId}/projects`, { project_id: projectId })
  },

  // 取消关联项目
  async removeFromProject(recordId, projectId) {
    return await client.delete(`/records/${recordId}/projects/${projectId}`)
  }
}

export default records
