<template>
  <el-menu
    :default-active="activeMenu"
    router
    class="app-sidebar"
  >
    <el-menu-item index="/">
      <el-icon><HomeFilled /></el-icon>
      <span>首页</span>
    </el-menu-item>
    
    <el-menu-item index="/records">
      <el-icon><Document /></el-icon>
      <span>记账</span>
    </el-menu-item>
    
    <el-menu-item index="/categories">
      <el-icon><Grid /></el-icon>
      <span>分类</span>
    </el-menu-item>
    
    <el-menu-item index="/budgets">
      <el-icon><Wallet /></el-icon>
      <span>预算</span>
    </el-menu-item>
    
    <el-menu-item index="/projects">
      <el-icon><Folder /></el-icon>
      <span>项目</span>
    </el-menu-item>
    
    <el-menu-item index="/statistics">
      <el-icon><TrendCharts /></el-icon>
      <span>统计</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  HomeFilled,
  Document,
  Grid,
  Wallet,
  Folder,
  TrendCharts
} from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.app-sidebar {
  height: 100%;
  border-right: none;
}
</style>
