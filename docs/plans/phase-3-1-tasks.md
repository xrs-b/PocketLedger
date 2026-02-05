# Phase 3-1: 项目初始化

## 任务概述
**Goal:** 初始化前端项目，安装 Element Plus、Pinia，配置 Axios 和 Router

## 任务清单

### Task 1: 安装依赖
- **Command:** npm install
- **Packages:** element-plus, pinia, axios, vue-router@4, @element-plus/icons-vue

### Task 2: 配置 Axios
- **File:** `frontend/src/api/client.js`
- **内容:**
  - Axios 实例配置
  - 请求拦截器（自动添加 Token）
  - 响应拦截器（401 处理）
  - 基础 URL 配置

### Task 3: 配置 Pinia
- **File:** `frontend/src/stores/index.js`
- **File:** `frontend/src/main.js`
- **内容:**
  - Pinia 实例化
  - 注册到 Vue

### Task 4: 配置 Vue Router
- **File:** `frontend/src/router/index.js`
- **File:** `frontend/src/router/guard.js`
- **内容:**
  - 路由配置
  - 路由守卫（需要登录的路由）

### Task 5: 搭建基础布局
- **File:** `frontend/src/App.vue`
- **File:** `frontend/src/style.css`
- **内容:**
  - Element Plus 样式引入
  - 基础 Layout 布局
  - 全局样式
