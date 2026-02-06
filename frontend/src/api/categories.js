import client from './client'

export const categories = {
  // 获取分类列表（支持筛选）
  async list(params = {}) {
    return await client.get('/categories', { params })
  },

  // 获取分类详情
  async get(id) {
    return await client.get(`/categories/${id}`)
  },

  // 创建分类
  async create(data) {
    return await client.post('/categories', data)
  },

  // 更新分类
  async update(id, data) {
    return await client.put(`/categories/${id}`, data)
  },

  // 删除分类
  async delete(id) {
    return await client.delete(`/categories/${id}`)
  },

  // 获取二级分类
  async getItems(parentId) {
    return await client.get('/categories/items', { params: { parent_id: parentId } })
  },

  // 获取系统预设分类
  async getPresets() {
    return await client.get('/categories/presets')
  }
}

export default categories
