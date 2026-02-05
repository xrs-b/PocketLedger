<template>
  <el-container class="basic-layout">
    <el-aside width="200px" v-if="authStore.isLoggedIn">
      <AppSidebar />
    </el-aside>
    <el-container>
      <el-header v-if="authStore.isLoggedIn">
        <AppHeader />
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'

const authStore = useAuthStore()
</script>

<style scoped>
.basic-layout {
  height: 100vh;
}
</style>
