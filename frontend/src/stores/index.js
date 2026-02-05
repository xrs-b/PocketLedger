import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useStore = defineStore('main', () => {
  // 状态
  const loading = ref(false)
  const sidebarCollapsed = ref(false)
  
  // actions
  function setLoading(value) {
    loading.value = value
  }
  
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
  
  return {
    loading,
    sidebarCollapsed,
    setLoading,
    toggleSidebar
  }
})
