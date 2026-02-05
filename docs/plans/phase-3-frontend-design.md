# Phase 3: 前端开发计划

**Goal:** 实现 PocketLedger 完整前端界面

**技术栈:**
- Vue 3 + Vite
- Element Plus (UI组件库)
- Pinia (状态管理)
- Vue Router
- Axios (API调用)

---

## 1. 技术架构

### 1.1 状态管理 (Pinia)
```text
stores/
├── auth.js          # 认证状态（token、用户信息）
├── categories.js    # 分类数据
├── records.js       # 记账记录
├── projects.js      # 项目数据
├── budgets.js      # 预算数据
└── ui.js            # UI状态（loading、toast等）
```

### 1.2 API 层
```text
api/
├── client.js        # Axios 实例（拦截器）
├── auth.js          # 认证相关 API
├── categories.js    # 分类 API
├── records.js       # 记账 API
├── projects.js      # 项目 API
├── budgets.js       # 预算 API
└── statistics.js    # 统计 API
```

### 1.3 路由结构
```text
router/
├── index.js        # 主路由配置
└── guard.js        # 路由守卫（token验证）
```

---

## 2. 页面结构

### 2.1 第一阶段：核心功能

#### 2.1.1 用户认证
- `Login.vue` - 登录页面
- `Register.vue` - 注册页面（需邀请码）

#### 2.1.2 记账首页
- `Home.vue` - 首页（今日记账入口）
- `RecordList.vue` - 记账列表
- `RecordForm.vue` - 新增/编辑记账
- `RecordDetail.vue` - 记账详情

#### 2.1.3 分类管理
- `Categories.vue` - 分类列表
- `CategoryForm.vue` - 新增/编辑分类

### 2.2 第二阶段：辅助功能

#### 2.2.1 预算管理
- `Budgets.vue` - 预算列表
- `BudgetForm.vue` - 新增/编辑预算
- `BudgetAlerts.vue` - 超支提醒

#### 2.2.2 项目管理
- `Projects.vue` - 项目列表
- `ProjectDetail.vue` - 项目详情
- `ProjectForm.vue` - 新增/编辑项目

### 2.3 第三阶段：统计报表

#### 2.3.1 统计页面
- `Statistics.vue` - 综合统计
- `MonthlyReport.vue` - 月度报表
- `CategoryChart.vue` - 分类占比图表
- `ProjectReport.vue` - 项目统计

---

## 3. 组件结构

### 3.1 公共组件
```text
components/
├── AppHeader.vue    # 顶部导航
├── AppSidebar.vue   # 侧边栏
├── RecordCard.vue   # 记账卡片
├── CategoryTag.vue  # 分类标签
├── AmountInput.vue  # 金额输入（支持小数）
├── DatePicker.vue   # 日期选择
├── EmptyState.vue   # 空状态提示
├── Loading.vue      # 加载动画
└── Toast.vue        # 轻提示
```

### 3.2 图表组件 (使用 ECharts)
```text
components/charts/
├── PieChart.vue     # 饼图（分类占比）
├── BarChart.vue     # 柱状图（月度对比）
├── LineChart.vue    # 折线图（趋势）
└── TrendChart.vue  # 收支趋势
```

---

## 4. 数据流设计

### 4.1 状态管理流程
```text
用户操作 → Component → Store Action → API 调用 → 更新 State → 响应式更新 Component
```

### 4.2 Token 刷新机制
- Axios 请求拦截器自动添加 Token
- 响应拦截器处理 401（Token过期）
- 401 时自动刷新 Token 或跳转登录

---

## 5. 错误处理

### 5.1 全局错误处理
- API 错误 → Toast 提示
- 网络错误 → 重试提示
- 权限错误 → 跳转登录

### 5.2 表单验证
- 使用 Element Plus 表单验证
- 必填项检查
- 金额格式验证
- 日期范围验证

---

## 6. 页面优先级

### 第一阶段：核心功能
1. ✅ 登录/注册页面（已有基础）
2. ✅ 记账 CRUD（核心核心）
3. ✅ 分类管理

### 第二阶段：辅助功能
4. ✅ 预算管理
5. ✅ 项目管理

### 第三阶段：统计报表
6. ✅ 数据统计

---

## 7. 开发计划

### 任务分解

#### Phase 3-1: 项目初始化
- 安装 Element Plus、Pinia
- 配置 Axios、Router
- 搭建基础布局

#### Phase 3-2: 认证模块
- 完善 Login.vue
- 完善 Register.vue
- 实现 Token 管理

#### Phase 3-3: 记账功能
- RecordList.vue
- RecordForm.vue
- 分类选择器

#### Phase 3-4: 分类管理
- Categories.vue
- CategoryForm.vue

#### Phase 3-5: 预算功能
- Budgets.vue
- BudgetAlerts.vue

#### Phase 3-6: 项目管理
- Projects.vue
- ProjectDetail.vue

#### Phase 3-7: 统计报表
- Statistics.vue
- ECharts 图表集成

---

## 8. 验证方法

```bash
# 启动开发服务器
npm run dev

# 运行测试
npm run test

# 构建生产版本
npm run build
```

---

## 9. 执行方式

**Subagent-Driven 开发：**
- 每个页面/组件作为一个独立任务
- TDD 模式：先写测试 → 实现 → 验证
- 每个任务独立提交

**验证标准：**
- 所有 API 调用正常工作
- 响应式数据更新正常
- 错误处理完善
- 移动端适配完成

---

## 下一步

准备开始 Phase 3-1：项目初始化

**确认此设计文档是否需要调整？**
