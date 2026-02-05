# PocketLedger Phase 2-3: 用户管理 & 邀请码

## 任务概述
**Goal:** 实现用户个人资料管理和邀请码功能

## 任务清单

### Task 1: 创建 Invitation 模型
- **File:** `backend/app/models/invitation.py`
- **Description:** 
  - id (PK)
  - code (unique string, 邀请码)
  - max_uses (int, 最大使用次数)
  - used_count (int, 已使用次数)
  - created_by_id (FK to User)
  - is_active (bool)
  - created_at (datetime)
  - expires_at (datetime, 可选)
- **Relationships:** Many-to-One with User (created_by)

### Task 2: 修改 User 模型
- **File:** `backend/app/models/user.py`
- **Description:** 添加 relationship 到 Invitation
- **Changes:** 添加 `invitations` relationship (one-to-many)

### Task 3: 创建 users router
- **File:** `backend/app/routers/users.py`
- **Description:** 用户管理 API 端点
- **Endpoints:**
  - `GET /api/v1/users/profile` - 获取个人资料
  - `PUT /api/v1/users/profile` - 更新个人资料
  - `GET /api/v1/users/invitations` - 获取我的邀请码
  - `POST /api/v1/users/invitations` - 创建邀请码

### Task 4: 创建用户测试
- **File:** `backend/tests/test_users.py`
- **Description:** 用户管理功能测试
- **Tests:**
  - 获取个人资料
  - 更新个人资料
  - 获取邀请码列表
  - 创建邀请码

### Task 5: 更新 main.py
- **File:** `backend/app/main.py`
- **Description:** 注册 users router
- **Changes:** 添加 `app.include_router(users.router, prefix="/api/v1")`

## 技术要求
- 遵循 TDD 开发模式
- 使用 JWT 认证
- 邀请码需要验证创建者身份
- 测试覆盖所有端点

## 验证方法
```bash
pytest tests/test_users.py -v
```
