# Phase 2-5: 记账记录 CRUD

## 任务概述
**Goal:** 实现记账记录管理功能

## 任务清单

### Task 1: 创建 Record 模型
- **File:** `backend/app/models/record.py`
- **Description:** 记账数据模型

### Task 2: 创建 Record Schemas
- **File:** `backend/app/schemas/record.py`
- **Description:** Pydantic schemas

### Task 3: 创建 Records Router
- **File:** `backend/app/routers/records.py`
- **Description:** 记账 CRUD 端点

### Task 4: 创建记账测试
- **File:** `backend/tests/test_records.py`
- **Description:** 记账功能测试

### Task 5: 更新 main.py
- **File:** `backend/app/main.py`
- **Description:** 注册 records router

## 功能要求
- 金额、人均消费计算
- AA 制分摊
- 备注字段
- 日期筛选
- 项目关联
