# Phase 2-7: 预算功能

## 任务概述
**Goal:** 实现预算管理功能

## 任务清单

### Task 1: 创建 Budget 模型
- **File:** `backend/app/models/budget.py`
- **Description:** 预算数据模型

### Task 2: 创建 Budget Schemas
- **File:** `backend/app/schemas/budget.py`
- **Description:** Pydantic schemas

### Task 3: 创建 Budgets Router
- **File:** `backend/app/routers/budgets.py`
- **Description:** 预算管理端点

### Task 4: 创建预算测试
- **File:** `backend/tests/test_budgets.py`
- **Description:** 预算功能测试

### Task 5: 更新 main.py
- **File:** `backend/app/main.py`
- **Description:** 注册 budgets router

## 功能要求
- 预算列表/创建/详情/更新/删除
- 超支提醒
- 按月预算
