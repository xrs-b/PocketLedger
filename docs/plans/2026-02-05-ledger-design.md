# 记账应用设计方案

**项目名称：** PocketLedger（口袋账本）  
**创建日期：** 2026-02-05  
**作者：** 小圆 & 老细

---

## 1. 项目概述

### 1.1 产品定位
一款面向情侣/家庭的轻量级记账应用，支持：
- 日常收支记录
- 项目型记账（装修、旅游等）
- 预算管理
- 多维度统计分析
- PWA移动端体验

### 1.2 核心用户故事
1. 作为用户，我可以用邀请码注册账号，保护隐私
2. 作为用户，我可以快速记录日常收支，选择分类
3. 作为用户，我可以创建项目（装修/旅游），在里面记录专项支出
4. 作为用户，我可以为单笔记录同时标记日常分类和项目
5. 作为用户，我可以设置项目预算，超支时获得提醒
6. 作为用户，我可以查看月度/时间段/项目的统计报告
7. 作为用户，我可以计算AA人均消费

---

## 2. 技术架构

### 2.1 技术栈

| 层级 | 技术选型 | 理由 |
|------|----------|------|
| 前端 | Vue 3 + Vite + TailwindCSS | 轻量、响应式、你熟悉 |
| 前端-状态管理 | Pinia | Vue 3官方推荐 |
| 前端-路由 | Vue Router | SPA路由 |
| 前端-PWA | Vite PWA Plugin | 离线缓存、安装到主屏幕 |
| 后端 | Python FastAPI | 异步高性能、自动文档 |
| 数据库 | MySQL 8.0 | 你熟悉、关系型数据 |
| 认证 | JWT + 邀请码 | 简单安全 |
| 部署 | Docker | 一键部署、跨平台 |

### 2.2 系统架构图

```
┌─────────────────────────────────────────────┐
│              用户设备（手机/PC）              │
│  ┌───────────────────────────────────────┐  │
│  │         Vue 3 PWA 前端应用             │  │
│  │  - 响应式布局（移动优先）               │  │
│  │  - Service Worker 离线缓存             │  │
│  │  - Web App Manifest 安装配置           │  │
│  └───────────────────────────────────────┘  │
│                      │                      │
│              HTTPS / REST API              │
│                      │                      │
│  ┌───────────────────────────────────────┐  │
│  │         FastAPI 后端服务              │  │
│  │  - /auth 认证模块                     │  │
│  │  - /api/v1/users 用户管理             │  │
│  │  - /api/v1/categories 分类管理        │  │
│  │  - /api/v1/records 记账记录          │  │
│  │  - /api/v1/projects 项目管理          │  │
│  │  - /api/v1/budgets 预算管理           │  │
│  │  - /api/v1/statistics 统计分析        │  │
│  └───────────────────────────────────────┘  │
│                      │                      │
│              MySQL (Docker)                │
│  ┌───────────────────────────────────────┐  │
│  │  - users 用户表                       │  │
│  │  - invitations 邀请码表               │  │
│  │  - categories 分类表                  │  │
│  │  - category_items 分类明细表          │  │
│  │  - projects 项目表                    │  │
│  │  - records 记账记录表                 │  │
│  │  - budgets 预算表                      │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
         │
         ▼
    docker-compose.yml
```

---

## 3. 数据库设计

### 3.1 ER 图

```
users ─────┬───── invitations
           │
           ├─── categories ───── category_items
           │
           ├─── projects ───── budgets
           │
           └─── records ───── project_records
```

### 3.2 详细表结构

#### 3.2.1 users 用户表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 用户ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| email | VARCHAR(100) | UNIQUE | 邮箱（可选） |
| avatar_url | VARCHAR(500) | NULL | 头像URL |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

#### 3.2.2 invitations 邀请码表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | ID |
| code | VARCHAR(20) | UNIQUE, NOT NULL | 邀请码 |
| max_uses | INT | DEFAULT 1 | 最大使用次数 |
| used_count | INT | DEFAULT 0 | 已使用次数 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| created_by | INT | FK(users.id) | 创建者 |
| expires_at | DATETIME | NULL | 过期时间 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 3.2.3 categories 分类表（一级分类）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 分类ID |
| user_id | INT | FK(users.id) | 所属用户 |
| name | VARCHAR(50) | NOT NULL | 分类名称 |
| type | ENUM('income', 'expense') | NOT NULL | 收入/支出 |
| icon | VARCHAR(50) | NULL | 图标名称 |
| color | VARCHAR(7) | NULL | 颜色代码 |
| sort_order | INT | DEFAULT 0 | 排序 |
| is_system | BOOLEAN | DEFAULT FALSE | 是否系统预设 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**系统预设分类（is_system=True）：**
- 收入：工资、奖金、投资、外快、其他收入
- 支出：
  - 餐饮：早餐、午餐、晚餐、下午茶、零食、奶茶
  - 交通：公交、地铁、打车、停车、油费
  - 娱乐：电影、游戏、旅游、演出
  - 景区：门票、住宿、餐饮
  - 购物：日用品、衣服、电子产品
  - 居住：房租、水电、物业
  - 医疗：看病、买药
  - 教育：学费、书籍、课程
  - 人情：红包、礼物
  - 其他

#### 3.2.4 category_items 分类明细表（二级分类）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | ID |
| category_id | INT | FK(categories.id) | 一级分类 |
| user_id | INT | FK(users.id) | 所属用户 |
| name | VARCHAR(50) | NOT NULL | 二级分类名称 |
| icon | VARCHAR(50) | NULL | 图标 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 3.2.5 projects 项目表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 项目ID |
| user_id | INT | FK(users.id) | 所属用户 |
| name | VARCHAR(100) | NOT NULL | 项目名称 |
| description | TEXT | NULL | 项目描述 |
| budget | DECIMAL(12,2) | NULL | 预算金额 |
| cover_image | VARCHAR(500) | NULL | 封面图 |
| status | ENUM('active', 'completed', 'archived') | DEFAULT 'active' | 状态 |
| start_date | DATE | NULL | 开始日期 |
| end_date | DATE | NULL | 结束日期 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

#### 3.2.6 budgets 预算表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 预算ID |
| user_id | INT | FK(users.id) | 所属用户 |
| project_id | INT | FK(projects.id), NULL | 关联项目（NULL=日常预算） |
| category_id | INT | FK(categories.id), NULL | 关联分类（NULL=总预算） |
| amount | DECIMAL(12,2) | NOT NULL | 预算金额 |
| period_type | ENUM('daily', 'weekly', 'monthly', 'yearly', 'custom') | DEFAULT 'monthly' | 周期类型 |
| period_start | DATE | NULL | 周期开始 |
| period_end | DATE | NULL | 周期结束 |
| alert_threshold | DECIMAL(5,2) | DEFAULT 80 | 提醒阈值（百分比） |
| is_active | BOOLEAN | DEFAULT TRUE | 是否启用 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

#### 3.2.7 records 记账记录表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 记录ID |
| user_id | INT | FK(users.id) | 所属用户 |
| amount | DECIMAL(12,2) | NOT NULL | 金额 |
| type | ENUM('income', 'expense') | NOT NULL | 收入/支出 |
| category_id | INT | FK(categories.id) | 一级分类 |
| category_item_id | INT | FK(category_items.id) | 二级分类 |
| payer_id | INT | FK(users.id) | 付款人 |
| participant_count | INT | DEFAULT 1 | 参与人数 |
| split_type | ENUM('single', 'aa', 'debt') | DEFAULT 'single' | 分摊方式 |
| debt_to | INT | FK(users.id), NULL | 欠款对象 |
| remark | VARCHAR(500) | NULL | 备注 |
| record_date | DATE | NOT NULL | 记录日期 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

#### 3.2.8 project_records 项目-记录关联表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | ID |
| project_id | INT | FK(projects.id) | 项目ID |
| record_id | INT | FK(records.id) | 记录ID |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

## 4. API 设计

### 4.1 认证模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /auth/register | 注册（需要邀请码） |
| POST | /auth/login | 登录 |
| POST | /auth/logout | 登出 |
| GET | /auth/me | 获取当前用户信息 |
| POST | /auth/refresh | 刷新Token |

### 4.2 用户模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/users/profile | 获取个人资料 |
| PUT | /api/v1/users/profile | 更新个人资料 |
| PUT | /api/v1/users/password | 修改密码 |
| GET | /api/v1/users/invitations | 获取我的邀请码 |
| POST | /api/v1/users/invitations | 创建邀请码 |

### 4.3 分类模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/categories | 获取分类列表 |
| POST | /api/v1/categories | 创建一级分类 |
| PUT | /api/v1/categories/{id} | 更新一级分类 |
| DELETE | /api/v1/categories/{id} | 删除一级分类 |
| GET | /api/v1/categories/items | 获取二级分类 |
| POST | /api/v1/categories/items | 创建二级分类 |
| PUT | /api/v1/categories/items/{id} | 更新二级分类 |
| DELETE | /api/v1/categories/items/{id} | 删除二级分类 |
| GET | /api/v1/categories/presets | 获取系统预设分类 |

### 4.4 项目模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/projects | 获取项目列表 |
| POST | /api/v1/projects | 创建项目 |
| GET | /api/v1/projects/{id} | 获取项目详情 |
| PUT | /api/v1/projects/{id} | 更新项目 |
| DELETE | /api/v1/projects/{id} | 删除项目 |
| GET | /api/v1/projects/{id}/budget | 获取项目预算 |
| PUT | /api/v1/projects/{id}/budget | 设置/更新项目预算 |
| GET | /api/v1/projects/{id}/stats | 获取项目统计 |

### 4.5 记账模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/records | 获取记录列表（支持筛选） |
| POST | /api/v1/records | 创建记录 |
| GET | /api/v1/records/{id} | 获取记录详情 |
| PUT | /api/v1/records/{id} | 更新记录 |
| DELETE | /api/v1/records/{id} | 删除记录 |
| POST | /api/v1/records/{id}/projects | 关联到项目 |
| DELETE | /api/v1/records/{id}/projects/{project_id} | 取消关联 |

### 4.6 预算模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/budgets | 获取预算列表 |
| POST | /api/v1/budgets | 创建预算 |
| GET | /api/v1/budgets/{id} | 获取预算详情 |
| PUT | /api/v1/budgets/{id} | 更新预算 |
| DELETE | /api/v1/budgets/{id} | 删除预算 |
| GET | /api/v1/budgets/alerts | 获取超支提醒 |

### 4.7 统计模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/statistics/monthly | 月度统计 |
| GET | /api/v1/statistics/range | 自定义时间段统计 |
| GET | /api/v1/statistics/categories | 分类占比统计 |
| GET | /api/v1/statistics/projects | 项目统计 |
| GET | /api/v1/statistics/overview | 综合概览 |

---

## 5. 前端设计

### 5.1 页面结构

```
pages/
├── Login.vue           # 登录页
├── Register.vue        # 注册页
├── Home.vue            # 首页（月度概览）
├── Records.vue         # 记账页
│   ├── RecordList.vue  # 记录列表
│   └── RecordForm.vue  # 记录表单
├── Projects.vue        # 项目列表
│   ├── ProjectList.vue
│   └── ProjectDetail.vue
├── Statistics.vue     # 统计页
│   ├── Monthly.vue     # 月度统计
│   ├── Category.vue    # 分类统计
│   └── Project.vue     # 项目统计
├── Budgets.vue         # 预算管理
├── Settings.vue        # 设置
│   ├── Profile.vue     # 个人资料
│   ├── Categories.vue  # 分类管理
│   └── Invitations.vue # 邀请码管理
└── components/
    ├── CategoryPicker.vue    # 分类选择器
    ├── AmountInput.vue       # 金额输入
    ├── DatePicker.vue        # 日期选择
    ├── ProjectSelector.vue   # 项目选择器
    ├── RecordCard.vue        # 记录卡片
    ├── StatCard.vue          # 统计卡片
    ├── BudgetProgress.vue     # 预算进度条
    └── Charts/               # 图表组件
```

### 5.2 核心交互流程

#### 5.2.1 快速记账流程

```
首页 (+ 按钮)
    ↓
选择类型（收入/支出）
    ↓
选择分类（一级 → 二级）
    ↓
输入金额
    ↓
输入日期、人数（可选）
    ↓
选择关联项目（可选）
    ↓
添加备注（可选）
    ↓
保存
```

#### 5.2.2 创建项目流程

```
项目页 (+ 按钮)
    ↓
输入项目名称
    ↓
输入描述（可选）
    ↓
设置预算（可选）
    ↓
选择开始/结束日期
    ↓
保存
```

### 5.3 响应式设计

- 移动端：单栏布局，底部Tab导航
- 平板/桌面：侧边栏 + 主内容区

### 5.4 PWA 配置

```javascript
// vite.config.js PWA 配置
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: '口袋账本',
        short_name: '账本',
        description: '轻量级情侣记账应用',
        theme_color: '#3B82F6',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}']
      }
    })
  ]
})
```

---

## 6. 部署方案

### 6.1 Docker Compose 配置

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: pocketledger-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: pocketledger
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql/init:/docker-entrypoint-initdb.d
    ports:
      - "3306:3306"
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: pocketledger-backend
    environment:
      - DATABASE_URL=mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mysql:3306/${MYSQL_DATABASE}
      - SECRET_KEY=${SECRET_KEY}
      - ACCESS_TOKEN_EXPIRE_MINUTES=60*24*7
    ports:
      - "8000:8000"
    depends_on:
      - mysql
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: pocketledger-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  mysql_data:
```

### 6.2 目录结构

```
pocketledger/
├── docker-compose.yml
├── .env
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── auth/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── categories.py
│   │   │   ├── records.py
│   │   │   ├── projects.py
│   │   │   ├── budgets.py
│   │   │   └── statistics.py
│   │   └── services/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── public/
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── package.json
│   └── Dockerfile
└── docs/
    └── plans/
        └── 2026-02-05-ledger-design.md
```

---

## 7. 开发计划

### Phase 1: 基础框架搭建
- [ ] 项目目录结构初始化
- [ ] Docker 环境搭建
- [ ] FastAPI 后端脚手架
- [ ] Vue 3 前端脚手架
- [ ] MySQL 数据库初始化
- [ ] JWT 认证系统

### Phase 2: 核心功能开发
- [ ] 分类管理（CRUD）
- [ ] 记账功能（CRUD）
- [ ] 项目管理（CRUD）
- [ ] 预算功能
- [ ] 统计分析 API

### Phase 3: 前端页面
- [ ] 登录/注册页面
- [ ] 首页概览
- [ ] 记账页面
- [ ] 项目页面
- [ ] 统计页面
- [ ] 设置页面

### Phase 4: PWA & 优化
- [ ] PWA 配置
- [ ] 离线缓存
- [ ] 响应式优化
- [ ] 性能优化

### Phase 5: 测试 & 部署
- [ ] 单元测试
- [ ] E2E 测试
- [ ] 生产环境部署
- [ ] HTTPS 配置

---

## 8. 附录

### 8.1 预设分类清单

**收入分类：**
1. 工资
2. 奖金
3. 投资
4. 外快
5. 其他收入

**支出分类：**

| 一级分类 | 二级分类 |
|----------|----------|
| 餐饮 | 早餐、午餐、晚餐、下午茶、零食、奶茶、其他 |
| 交通 | 公交、地铁、打车、停车、油费、高速、其他 |
| 娱乐 | 电影、游戏、旅游、演出、运动、其他 |
| 景区 | 门票、住宿、餐饮、购物、交通、其他 |
| 购物 | 日用品、衣服、鞋子、包包、电子产品、化妆品、其他 |
| 居住 | 房租、水电、物业、装修、家居、其他 |
| 医疗 | 看病、买药、体检、保健、其他 |
| 教育 | 学费、书籍、课程、培训、其他 |
| 人情 | 红包、礼物、喜酒、其他 |
| 其他 | - |

### 8.2 状态码规范

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 422 | 验证错误 |
| 500 | 服务器错误 |

---

**文档版本：** 1.0  
**最后更新：** 2026-02-05
