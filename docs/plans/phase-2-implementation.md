# Phase 2: 核心功能实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 实现 PocketLedger 核心功能：用户认证、分类管理、记账记录、项目管理、预算功能

**Architecture:** 采用 FastAPI RESTful API + Vue 3 SPA + MySQL，遵循 TDD 开发模式

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, Vue 3, Pinia, TailwindCSS

---

## 任务清单

### Phase 2-1: 数据库模型 & 配置

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/category.py`
- Create: `backend/app/models/record.py`
- Create: `backend/app/models/project.py`
- Create: `backend/app/models/budget.py`
- Create: `backend/app/database.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_models.py`

---

### Phase 2-2: 认证系统 (JWT + 邀请码)

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/auth/__init__.py`
- Create: `backend/app/auth/jwt.py`
- Create: `backend/app/auth/password.py`
- Create: `backend/app/routers/auth.py`
- Create: `backend/tests/test_auth.py`

**Endpoints:**
- `POST /auth/register` - 用户注册（需邀请码）
- `POST /auth/login` - 用户登录
- `POST /auth/logout` - 登出
- `GET /auth/me` - 获取当前用户
- `POST /auth/refresh` - 刷新 Token

---

### Phase 2-3: 用户管理 & 邀请码

**Files:**
- Create: `backend/app/routers/users.py`
- Modify: `backend/app/models/user.py`
- Create: `backend/app/models/invitation.py`
- Create: `backend/tests/test_users.py`

**Endpoints:**
- `GET /api/v1/users/profile` - 获取个人资料
- `PUT /api/v1/users/profile` - 更新个人资料
- `GET /api/v1/users/invitations` - 获取我的邀请码
- `POST /api/v1/users/invitations` - 创建邀请码

---

### Phase 2-4: 分类管理 (两级分类)

**Files:**
- Create: `backend/app/routers/categories.py`
- Create: `backend/app/models/category.py`
- Create: `backend/app/schemas/category.py`
- Create: `backend/tests/test_categories.py`

**Endpoints:**
- `GET /api/v1/categories` - 获取一级分类列表
- `POST /api/v1/categories` - 创建一级分类
- `PUT /api/v1/categories/{id}` - 更新分类
- `DELETE /api/v1/categories/{id}` - 删除分类
- `GET /api/v1/categories/items` - 获取二级分类
- `POST /api/v1/categories/items` - 创建二级分类
- `GET /api/v1/categories/presets` - 获取系统预设分类

**预设分类:**
- 收入：工资、奖金、投资、外快、其他收入
- 支出：餐饮、交通、娱乐、景区、购物、居住、医疗、教育、人情、其他

---

### Phase 2-5: 记账记录 CRUD

**Files:**
- Create: `backend/app/routers/records.py`
- Create: `backend/app/models/record.py`
- Create: `backend/app/schemas/record.py`
- Create: `backend/tests/test_records.py`

**Endpoints:**
- `GET /api/v1/records` - 获取记录列表（支持筛选）
- `POST /api/v1/records` - 创建记录
- `GET /api/v1/records/{id}` - 获取记录详情
- `PUT /api/v1/records/{id}` - 更新记录
- `DELETE /api/v1/records/{id}` - 删除记录
- `POST /api/v1/records/{id}/projects` - 关联到项目
- `DELETE /api/v1/records/{id}/projects/{project_id}` - 取消关联

**功能:**
- 金额、人数、人均消费计算
- AA 制分摊
- 备注字段
- 日期筛选

---

### Phase 2-6: 项目管理

**Files:**
- Create: `backend/app/routers/projects.py`
- Create: `backend/app/models/project.py`
- Create: `backend/app/schemas/project.py`
- Create: `backend/tests/test_projects.py`

**Endpoints:**
- `GET /api/v1/projects` - 获取项目列表
- `POST /api/v1/projects` - 创建项目
- `GET /api/v1/projects/{id}` - 获取项目详情
- `PUT /api/v1/projects/{id}` - 更新项目
- `DELETE /api/v1/projects/{id}` - 删除项目
- `GET /api/v1/projects/{id}/stats` - 获取项目统计

---

### Phase 2-7: 预算功能

**Files:**
- Create: `backend/app/routers/budgets.py`
- Create: `backend/app/models/budget.py`
- Create: `backend/app/schemas/budget.py`
- Create: `backend/tests/test_budgets.py`

**Endpoints:**
- `GET /api/v1/budgets` - 获取预算列表
- `POST /api/v1/budgets` - 创建预算
- `GET /api/v1/budgets/{id}` - 获取预算详情
- `PUT /api/v1/budgets/{id}` - 更新预算
- `DELETE /api/v1/budgets/{id}` - 删除预算
- `GET /api/v1/budgets/alerts` - 获取超支提醒

---

### Phase 2-8: 统计分析 API

**Files:**
- Create: `backend/app/routers/statistics.py`
- Create: `backend/tests/test_statistics.py`

**Endpoints:**
- `GET /api/v1/statistics/monthly` - 月度统计
- `GET /api/v1/statistics/range` - 自定义时间段统计
- `GET /api/v1/statistics/categories` - 分类占比统计
- `GET /api/v1/statistics/projects` - 项目统计
- `GET /api/v1/statistics/overview` - 综合概览

---

## 验证方法

**Backend 测试:**
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

**API 验证:**
```bash
# 启动服务
uvicorn main:app --reload

# 测试健康检查
curl http://localhost:8000/api/v1/health

# 测试 API 文档
# 访问 http://localhost:8000/docs
```

---

## 执行方式选择

**Plan complete and saved to `docs/plans/phase-2-implementation.md`. Two execution options:**

**1. Subagent-Driven (this session)** - 我 dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**

---

**如果选择 Subagent-Driven:**
- **REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development
- Stay in this session
- Fresh subagent per task + code review
- 每个任务遵循 TDD（先写测试 → 测试失败 → 写代码 → 测试通过 → commit）

**如果选择 Parallel Session:**
- Guide them to open new session in worktree
- **REQUIRED SUB-SKILL:** New session uses superpowers:executing-plans
- 批量执行任务，中间有 checkpoint 检查
