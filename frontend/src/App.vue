<template>
  <el-config-provider :locale="locale">
    <div class="app-container">
      <!-- 已登录：显示完整布局 -->
      <template v-if="authStore.isLoggedIn">
        <AppHeader />
        <div class="app-content">
          <AppSidebar />
          <main class="main-content">
            <router-view />
          </main>
        </div>
      </template>
      
      <!-- 未登录：只显示路由内容 -->
      <template v-else>
        <router-view />
      </template>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref } from 'vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import AppHeader from '@/components/AppHeader.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import { useAuthStore } from '@/stores/auth'

const locale = ref(zhCn)
const authStore = useAuthStore()
</script>

<style>
@import 'element-plus/dist/index.css'

html, body, #app {
  height: 100%;
  margin: 0;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-content {
  display: flex;
  flex: 1;
}

.main-content {
  flex: 1;
  padding: 20px;
  background-color: #f5f7fa;
  overflow-y: auto;
}
</style>
