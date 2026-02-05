import { defineStore } from 'pinia'
import { ref } from 'vue'

// API 基础路径
const API_BASE = '/api'

export const useCategoriesStore = defineStore('categories', () => {
  // 状态
  const categories = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const incomeCategories = ref([])
  const expenseCategories = ref([])
  const totalCount = ref(0)

  // Actions

  /**
   * 获取所有分类
   */
  const fetchCategories = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${API_BASE}/categories`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data.code === 0) {
        categories.value = data.data || []
        updateGetters()
      } else {
        throw new Error(data.message || '获取分类失败')
      }
    } catch (err) {
      console.error('获取分类失败:', err)
      error.value = err.message
      
      // 使用模拟数据作为后备（开发阶段）
      useMockData()
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建新分类
   * @param {Object} categoryData - 分类数据
   */
  const createCategory = async (categoryData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${API_BASE}/categories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(categoryData)
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data.code === 0) {
        // 添加到列表
        const newCategory = data.data
        
        if (categoryData.parentId) {
          // 子分类：添加到对应父分类的 children 中
          const parentIndex = categories.value.findIndex(
            cat => cat.id === categoryData.parentId
          )
          if (parentIndex !== -1) {
            if (!categories.value[parentIndex].children) {
              categories.value[parentIndex].children = []
            }
            categories.value[parentIndex].children.push(newCategory)
          }
        } else {
          // 一级分类
          categories.value.push(newCategory)
        }
        
        updateGetters()
        return newCategory
      } else {
        throw new Error(data.message || '创建分类失败')
      }
    } catch (err) {
      console.error('创建分类失败:', err)
      error.value = err.message
      
      // 开发阶段：使用模拟数据
      const mockCategory = {
        id: Date.now(),
        ...categoryData,
        isPreset: false,
        children: []
      }
      
      if (categoryData.parentId) {
        const parentIndex = categories.value.findIndex(
          cat => cat.id === categoryData.parentId
        )
        if (parentIndex !== -1) {
          if (!categories.value[parentIndex].children) {
            categories.value[parentIndex].children = []
          }
          categories.value[parentIndex].children.push(mockCategory)
        }
      } else {
        categories.value.push(mockCategory)
      }
      
      updateGetters()
      return mockCategory
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新分类
   * @param {Object} categoryData - 分类数据（包含 id）
   */
  const updateCategory = async (categoryData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${API_BASE}/categories/${categoryData.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(categoryData)
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data.code === 0) {
        // 更新本地数据
        updateCategoryInList(categoryData)
        updateGetters()
        return data.data
      } else {
        throw new Error(data.message || '更新分类失败')
      }
    } catch (err) {
      console.error('更新分类失败:', err)
      error.value = err.message
      
      // 开发阶段：使用模拟数据
      updateCategoryInList(categoryData)
      updateGetters()
      return categoryData
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除分类
   * @param {number|string} categoryId - 分类 ID
   */
  const deleteCategory = async (categoryId) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${API_BASE}/categories/${categoryId}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data.code === 0) {
        // 从本地移除
        removeCategoryFromList(categoryId)
        updateGetters()
        return true
      } else {
        throw new Error(data.message || '删除分类失败')
      }
    } catch (err) {
      console.error('删除分类失败:', err)
      error.value = err.message
      
      // 开发阶段：使用模拟数据
      removeCategoryFromList(categoryId)
      updateGetters()
      return true
    } finally {
      loading.value = false
    }
  }

  // 辅助方法：从列表中更新分类
  const updateCategoryInList = (updatedCategory) => {
    const updateInTree = (tree) => {
      tree.forEach((cat, index) => {
        if (cat.id === updatedCategory.id) {
          tree[index] = { ...cat, ...updatedCategory }
        }
        if (cat.children) {
          updateInTree(cat.children)
        }
      })
    }
    updateInTree(categories.value)
  }

  // 辅助方法：从列表中移除分类
  const removeCategoryFromList = (categoryId) => {
    const removeFromTree = (tree) => {
      for (let i = tree.length - 1; i >= 0; i--) {
        const cat = tree[i]
        
        if (cat.id === categoryId) {
          // 找到并删除
          tree.splice(i, 1)
          return true
        }
        
        if (cat.children) {
          if (removeFromTree(cat.children)) {
            // 如果父分类没有子分类了，删除 children 数组
            if (cat.children.length === 0) {
              delete cat.children
            }
            return true
          }
        }
      }
      return false
    }
    removeFromTree(categories.value)
  }

  // 辅助方法：更新计算属性
  const updateGetters = () => {
    incomeCategories.value = categories.value.filter(cat => cat.type === 'income')
    expenseCategories.value = categories.value.filter(cat => cat.type === 'expense')
    
    totalCount.value = categories.value.reduce((total, cat) => {
      return total + 1 + (cat.children?.length || 0)
    }, 0)
  }

  // 辅助方法：使用模拟数据（开发阶段）
  const useMockData = () => {
    categories.value = [
      {
        id: 1,
        name: '收入',
        type: 'income',
        isPreset: true,
        children: [
          { id: 11, name: '工资', parentId: 1, type: 'income', icon: 'Money', isPreset: true },
          { id: 12, name: '奖金', parentId: 1, type: 'income', icon: 'Gift', isPreset: true },
          { id: 13, name: '投资', parentId: 1, type: 'income', icon: 'TrendCharts', isPreset: false }
        ]
      },
      {
        id: 2,
        name: '支出',
        type: 'expense',
        isPreset: true,
        children: [
          { id: 21, name: '餐饮', parentId: 2, type: 'expense', icon: 'Food', isPreset: true },
          { id: 22, name: '交通', parentId: 2, type: 'expense', icon: 'Van', isPreset: true },
          { id: 23, name: '购物', parentId: 2, type: 'expense', icon: 'ShoppingCart', isPreset: true },
          { id: 24, name: '娱乐', parentId: 2, type: 'expense', icon: 'Film', isPreset: false }
        ]
      }
    ]
    updateGetters()
  }

  /**
   * 重置状态
   */
  const reset = () => {
    categories.value = []
    loading.value = false
    error.value = null
    incomeCategories.value = []
    expenseCategories.value = []
    totalCount.value = 0
  }

  return {
    // 状态
    categories,
    loading,
    error,
    
    // Getters
    incomeCategories,
    expenseCategories,
    totalCount,
    
    // Actions
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    reset
  }
})
