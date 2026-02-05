import client from './client'

export const projects = {
  // 获取项目列表（支持筛选）
  async list(params = {}) {
    return await client.get('/projects', { params })
  },

  // 获取项目详情
  async get(id) {
    return await client.get(`/projects/${id}`)
  },

  // 创建项目
  async create(data) {
    return await client.post('/projects', data)
  },

  // 更新项目
  async update(id, data) {
    return await client.put(`/projects/${id}`, data)
  },

  // 删除项目
  async delete(id) {
    return await client.delete(`/projects/${id}`)
  },

  // 获取项目统计
  async getStats(id) {
    return await client.get(`/projects/${id}/stats`)
  },

  // 获取项目记账记录
  async getRecords(id, params = {}) {
    return await client.get(`/projects/${id}/records`, { params })
  },

  // 将记账关联到项目
  async addRecord(projectId, recordId) {
    return await client.post(`/projects/${projectId}/records`, { record_id: recordId })
  },

  // 取消关联
  async removeRecord(projectId, recordId) {
    return await client.delete(`/projects/${projectId}/records/${recordId}`)
  }
}

export default projects
