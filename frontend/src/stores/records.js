import { defineStore } from 'pinia'
import { ref } from 'vue'
import { records as recordsApi } from '@/api/records'

export const useRecordsStore = defineStore('records', () => {
  // 状态
  const records = ref([])
  const loading = ref(false)
  const currentRecord = ref(null)

  // Actions
  async function fetchRecords(params = {}) {
    loading.value = true
    try {
      const response = await recordsApi.list(params)
      records.value = response
      return response
    } catch (error) {
      console.error('获取记录列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchRecord(id) {
    loading.value = true
    try {
      const response = await recordsApi.get(id)
      currentRecord.value = response
      return response
    } catch (error) {
      console.error('获取记录详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function createRecord(data) {
    loading.value = true
    try {
      const response = await recordsApi.create(data)
      records.value.unshift(response)
      return response
    } catch (error) {
      console.error('创建记录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function updateRecord(id, data) {
    loading.value = true
    try {
      const response = await recordsApi.update(id, data)
      const index = records.value.findIndex(r => r.id === id)
      if (index !== -1) {
        records.value[index] = response
      }
      if (currentRecord.value?.id === id) {
        currentRecord.value = response
      }
      return response
    } catch (error) {
      console.error('更新记录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function deleteRecord(id) {
    loading.value = true
    try {
      await recordsApi.delete(id)
      records.value = records.value.filter(r => r.id !== id)
      if (currentRecord.value?.id === id) {
        currentRecord.value = null
      }
    } catch (error) {
      console.error('删除记录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 关联到项目
  async function addToProject(recordId, projectId) {
    loading.value = true
    try {
      const response = await recordsApi.addToProject(recordId, projectId)
      const record = records.value.find(r => r.id === recordId)
      if (record) {
        record.projects = record.projects || []
        record.projects.push({ id: projectId })
      }
      return response
    } catch (error) {
      console.error('关联项目失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 从项目移除
  async function removeFromProject(recordId, projectId) {
    loading.value = true
    try {
      await recordsApi.removeFromProject(recordId, projectId)
      const record = records.value.find(r => r.id === recordId)
      if (record?.projects) {
        record.projects = record.projects.filter(p => p.id !== projectId)
      }
    } catch (error) {
      console.error('取消关联项目失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 清空记录列表
  function clearRecords() {
    records.value = []
    currentRecord.value = null
  }

  return {
    records,
    loading,
    currentRecord,
    fetchRecords,
    fetchRecord,
    createRecord,
    updateRecord,
    deleteRecord,
    addToProject,
    removeFromProject,
    clearRecords
  }
})

export default useRecordsStore
