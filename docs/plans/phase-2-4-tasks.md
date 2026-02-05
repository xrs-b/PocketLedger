# Phase 2-4: 分类管理 (两级分类)

## 任务概述
**Goal:** 实现两级分类管理功能

## 任务清单

### Task 1: 创建 Category 模型
- **File:** `backend/app/models/category.py`
- **Description:** 
  - 一级分类 + 二级分类支持
  - 分类类型（收入/支出）

### Task 2: 创建 Category Schemas
- **File:** `backend/app/schemas/category.py`
- **Description:** Pydantic schemas

### Task 3: 创建 Categories Router
- **File:** `backend/app/routers/categories.py`
- **Description:** 分类 CRUD 端点

### Task 4: 创建分类测试
- **File:** `backend/tests/test_categories.py`
- **Description:** 分类功能测试

### Task 5: 更新 main.py
- **File:** `backend/app/main.py`
- **Description:** 注册 categories router

## 技术要求
- 两级分类结构（一级 + 二级）
- 分类类型：收入/支出
- 预设分类（系统默认）
- TDD 开发模式
