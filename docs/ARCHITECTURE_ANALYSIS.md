# PocketLedger 技术分析与重构方案

## 1. 404 问题的根本原因分析

### 问题现象
- 前端所有 API 请求返回 404
- 后端直接测试 `/api/v1/health` 正常
- 后端路由注册正确 (`/api/v1/auth/login` POST)

### 根因分析

#### 根因 1：OAuth2PasswordRequestForm 与 JSON 格式不兼容

**后端代码** (`backend/app/routers/auth.py`):
```python
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
```

**问题**：`OAuth2PasswordRequestForm` 是 FastAPI 的 OAuth2 标准实现，**期望 form-data 格式**（`application/x-www-form-urlencoded`），不支持 JSON！

**前端代码** (`frontend/src/api/auth.js`):
```javascript
export const login = (data) => {
  return client.post('/auth/login', {
    email: data.email,
    password: data.password
  })
}
```

前端发送 JSON：`{"email": "test@test.com", "password": "test"}`
但后端期望 form-data：`username=test@test.com&password=test`

**这就是所有 POST 请求返回 404 的原因！**

#### 根因 2：API 路由前缀配置不一致

| 组件 | 前缀配置 |
|------|----------|
| main.py | `prefix="/api/v1"` |
| auth.py | `prefix="/auth"` |
| 前端 client.js | `baseURL: '/api/v1'` |

完整路径：`/api/v1/auth/login`

---

## 2. 项目架构分析

### 当前架构问题

```
┌─────────────────────────────────────────────────────────────┐
│                      前端 (Vue 3)                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ src/api/client.js (axios, baseURL: '/api/v1')      │    │
│  │ src/views/Login.vue → auth.js → client.post()      │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ Nginx 代理
┌─────────────────────────────────────────────────────────────┐
│                      后端 (FastAPI)                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ main.py (include_router with prefix="/api/v1")    │    │
│  │ routers/auth.py (prefix="/auth", OAuth2Password)  │    │
│  │ OAuth2PasswordRequestForm (form-data only!)       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    数据库 (MySQL 8.0)                        │
└─────────────────────────────────────────────────────────────┘
```

### 架构问题总结

1. **前后端通信协议不匹配**
   - 后端：OAuth2PasswordRequestForm (form-data)
   - 前端：JSON
   - 结果：404

2. **Docker 部署复杂**
   - 3 个容器 (frontend, backend, db)
   - Nginx 需要正确配置代理
   - 网络配置容易出错

3. **依赖缺失**
   - `pytz` 缺失 (导致 auth 路由导入失败)
   - `email-validator` 缺失 (导致 schemas 导入失败)

---

## 3. 重构方案

### 方案 A：修改后端支持 JSON（推荐，快速修复）

修改 `backend/app/routers/auth.py`:

```python
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login", response_model=Token)
async def login(
    request: LoginRequest,  # ← 改为 JSON
    db: Session = Depends(get_db)
):
    # 通过 email 查找用户
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(...)
    
    # ... 其余代码
```

**优点**：
- 改动最小
- 符合前后端分离惯例
- 前端无需修改

**缺点**：
- 破坏 OAuth2 标准

---

### 方案 B：修改前端发送 form-data（符合标准）

修改 `frontend/src/api/auth.js`:

```javascript
export const login = (data) => {
  return client.post('/auth/login', 
    new URLSearchParams({
      username: data.email,  // OAuth2 用 username 字段
      password: data.password
    }), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}
```

**优点**：
- 符合 OAuth2 标准
- 后端无需修改

**缺点**：
- 前端需要特殊处理
- 不够直观

---

### 方案 C：前后端分离 + 独立部署（推荐，长期方案）

简化部署架构：

```
部署选项 1: 最小化部署 (推荐)
├── MySQL (Docker)
└── 后端 (Python venv + Gunicorn/Uvicorn)

部署选项 2: 完整 Docker 部署
├── MySQL (Docker)
├── 后端 (Docker)
└── 前端 (Nginx 静态文件)

部署选项 3: 开发模式
├── MySQL (Docker)
├── 后端 (Python venv + uvicorn --reload)
└── 前端 (Vite dev server)
```

---

## 4. 推荐的修复步骤

### 第一步：修复 JSON 登录 (5 分钟)

```bash
# 修改 backend/app/routers/auth.py
# 1. 添加 LoginRequest Schema
# 2. 修改 login 函数签名
# 3. 通过 email 而非 username 查找用户

# 修改 frontend/src/api/auth.js
# 保持 JSON 格式发送
```

### 第二步：修复 Docker 依赖

```bash
# backend/requirements.txt 添加
pytz==2025.2
email-validator==2.1.0
httpx==0.26.0  # 用于测试
requests==2.31.0  # 用于测试
```

### 第三步：简化部署配置

```yaml
# docker-compose.yml 简化版本
services:
  mysql:
    image: mysql:8.0
    ports: ["3306:3306"]
    
  backend:
    build: backend
    ports: ["8000:8000"]
    depends_on: [mysql]
    
  frontend:
    build: frontend
    ports: ["80:80"]
    depends_on: [backend]
```

### 第四步：添加健康检查

```python
# backend/app/main.py
@app.get("/health")
async def health():
    return {"status": "ok", "database": "connected"}
```

---

## 5. 技术学习总结

### Vue + Python 前后端分离最佳实践

#### 前端 → 后端通信

| 场景 | Content-Type | 示例 |
|------|--------------|------|
| 登录 (OAuth2) | `application/x-www-form-urlencoded` | `username=email&password=xxx` |
| 其他 API | `application/json` | `{"email": "x@x.com", "data": "xxx"}` |

#### FastAPI 安全组件选择

| 组件 | 用途 | 数据格式 |
|------|------|----------|
| `OAuth2PasswordRequestForm` | OAuth2 标准登录 | form-data |
| `Form(...)` | 普通表单 | form-data |
| `BaseModel` + Pydantic | JSON API | JSON |

#### Docker 部署要点

1. **依赖完整**: `requirements.txt` 包含所有 Python 依赖
2. **网络配置**: 确保容器在同一网络
3. **端口映射**: 正确映射端口
4. **健康检查**: 添加健康端点

---

## 6. 行动计划

- [ ] 修复 `backend/app/routers/auth.py` - 支持 JSON 登录
- [ ] 更新 `backend/requirements.txt` - 补充缺失依赖
- [ ] 更新 `frontend/src/api/auth.js` - 确保 JSON 格式
- [ ] 测试本地开发环境
- [ ] 更新 Docker 配置
- [ ] 创建部署文档
- [ ] 测试云服务器部署

---

*生成时间: 2026-02-06*
