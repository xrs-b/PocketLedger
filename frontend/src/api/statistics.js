import client from './client'

export const statistics = {
  // 获取概览统计
  async getOverview(params = {}) {
    return await client.get('/statistics/overview', { params })
  },

  // 获取月度统计
  async getMonthly(year, month) {
    return await client.get('/statistics/monthly', { params: { year, month } })
  },

  // 获取时间段统计
  async getRange(date_from, date_to) {
    return await client.get('/statistics/range', { params: { date_from, date_to } })
  },

  // 获取分类统计
  async getCategories(params = {}) {
    return await client.get('/statistics/categories', { params })
  },

  // 获取项目统计
  async getProjects(params = {}) {
    return await client.get('/statistics/projects', { params })
  }
}

export default statistics
