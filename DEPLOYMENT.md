# PocketLedger 完整部署指南

## 📋 项目概览

**PocketLedger** - 轻量级情侣/个人记账 Web 应用

### 技术栈
- **前端**: Vue 3 + Vite + Element Plus + Pinia + TailwindCSS + PWA
- **后端**: Python FastAPI + SQLAlchemy + Pydantic
- **数据库**: MySQL 8.0
- **部署**: Docker + Docker Compose

### 功能特性
- ✅ 用户认证 (JWT + 邀请码注册)
- ✅ 日常收支记账 (支持 AA 制)
- ✅ 项目型记账 (装修、旅游等)
- ✅ 预算管理 (带超支提醒)
- ✅ 多维度统计分析
- ✅ 二级分类管理

---

## 🏗️ 项目结构

```
PocketLedger/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── models/            # 数据模型 (6个)
│   │   │   ├── user.py        # 用户模型
│   │   │   ├── category.py    # 分类模型
│   │   │   ├── record.py      # 记账记录模型
│   │   │   ├── project.py     # 项目模型
│   │   │   ├── budget.py      # 预算模型
│   │   │   └── invitation.py  # 邀请码模型
│   │   ├── routers/           # API 路由 (7个模块)
│   │   │   ├── auth.py        # 认证路由 (/auth)
│   │   │   ├── users.py       # 用户路由 (/users)
│   │   │   ├── categories.py  # 分类路由 (/categories)
│   │   │   ├── records.py     # 记账路由 (/records)
│   │   │   ├── projects.py    # 项目路由 (/projects)
│   │   │   ├── budgets.py     # 预算路由 (/budgets)
│   │   │   └── statistics.py  # 统计路由 (/statistics)
│   │   ├── schemas/           # Pydantic 模式
│   │   ├── auth/              # JWT 认证模块
│   │   ├── main.py            # FastAPI 入口
│   │   ├── database.py        # 数据库配置
│   │   └── config.py          # 配置管理
│   ├── Dockerfile             # 后端 Docker 镜像
│   ├── init_db.py             # 数据库初始化脚本
│   └── requirements.txt       # Python 依赖
│
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── views/             # 页面 (11个)
│   │   │   ├── Login.vue      # 登录页面
│   │   │   ├── Register.vue   # 注册页面
│   │   │   ├── Home.vue       # 首页
│   │   │   ├── RecordList.vue # 记账列表
│   │   │   ├── RecordForm.vue # 记账表单
│   │   │   ├── RecordDetail.vue # 记账详情
│   │   │   ├── Categories.vue # 分类管理
│   │   │   ├── Budgets.vue    # 预算管理
│   │   │   ├── Projects.vue   # 项目列表
│   │   │   ├── ProjectDetail.vue # 项目详情
│   │   │   └── Statistics.vue # 统计报表
│   │   ├── components/        # 公共组件 (7个)
│   │   │   ├── RecordCard.vue  # 记账卡片
│   │   │   ├── CategoryTag.vue # 分类标签
│   │   │   ├── EmptyState.vue  # 空状态
│   │   │   ├── AppHeader.vue   # 顶部导航
│   │   │   ├── AppSidebar.vue  # 侧边栏
│   │   │   └── charts/        # ECharts 图表
│   │   ├── api/               # API 调用层 (7个)
│   │   │   ├── client.js      # Axios 实例
│   │   │   ├── auth.js        # 认证 API
│   │   │   ├── users.js       # 用户 API
│   │   │   ├── categories.js  # 分类 API
│   │   │   ├── records.js     # 记账 API
│   │   │   ├── projects.js    # 项目 API
│   │   │   ├── budgets.js     # 预算 API
│   │   │   └── statistics.js  # 统计 API
│   │   ├── stores/            # Pinia 状态管理
│   │   │   ├── auth.js        # 认证状态
│   │   │   └── records.js     # 记账状态
│   │   └── router/            # Vue Router 配置
│   ├── Dockerfile             # 前端 Docker 镜像
│   ├── nginx.conf             # Nginx 配置
│   └── package.json           # Node 依赖
│
├── docker-compose.yml         # Docker Compose 配置
└── README.md                  # 项目说明
```

---

## 🔧 API 端点清单

### 认证模块 (`/api/v1/auth`)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 (需要邀请码) |
| POST | `/api/v1/auth/login` | 用户登录 |
| POST | `/api/v1/auth/logout` | 退出登录 |
| GET | `/api/v1/auth/me` | 获取当前用户 |

### 用户模块 (`/api/v1/users`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/users/profile` | 获取个人资料 |
| PUT | `/api/v1/users/profile` | 更新个人资料 |
| GET | `/api/v1/users/invitations` | 获取我的邀请码 |
| POST | `/api/v1/users/invitations` | 创建邀请码 |

### 分类模块 (`/api/v1/categories`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/categories` | 获取分类列表 |
| POST | `/api/v1/categories` | 创建分类 |
| PUT | `/api/v1/categories/{id}` | 更新分类 |
| DELETE | `/api/v1/categories/{id}` | 删除分类 |

### 记账模块 (`/api/v1/records`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/records` | 获取记录列表 |
| POST | `/api/v1/records` | 创建记录 |
| GET | `/api/v1/records/{id}` | 获取记录详情 |
| PUT | `/api/v1/records/{id}` | 更新记录 |
| DELETE | `/api/v1/records/{id}` | 删除记录 |

### 项目模块 (`/api/v1/projects`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/projects` | 获取项目列表 |
| POST | `/api/v1/projects` | 创建项目 |
| GET | `/api/v1/projects/{id}` | 获取项目详情 |
| PUT | `/api/v1/projects/{id}` | 更新项目 |
| DELETE | `/api/v1/projects/{id}` | 删除项目 |

### 预算模块 (`/api/v1/budgets`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/budgets` | 获取预算列表 |
| POST | `/api/v1/budgets` | 创建预算 |
| GET | `/api/v1/budgets/{id}` | 获取预算详情 |
| PUT | `/api/v1/budgets/{id}` | 更新预算 |
| DELETE | `/api/v1/budgets/{id}` | 删除预算 |
| GET | `/api/v1/budgets/alerts` | 获取超支提醒 |

### 统计模块 (`/api/v1/statistics`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/statistics/monthly` | 月度统计 |
| GET | `/api/v1/statistics/range` | 自定义时间段统计 |
| GET | `/api/v1/statistics/categories` | 分类占比统计 |
| GET | `/api/v1/statistics/projects` | 项目统计 |
| GET | `/api/v1/statistics/overview` | 综合概览 |

---

## 🚀 Ubuntu 24.04 完整部署教程

### 第一步：系统准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install -y curl git wget unzip
```

### 第二步：安装 Docker

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 添加用户到 docker 组 (免 sudo)
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo apt install docker-compose -y

# 验证安装
docker --version
docker-compose --version
```

### 第三步：克隆项目

```bash
# 创建项目目录
mkdir -p /var/www
cd /var/www

# 克隆项目 (HTTPS 方式)
git clone https://github.com/xrs-b/PocketLedger.git
cd PocketLedger

# 或者使用 SSH (如果已配置)
# git clone git@github.com:xrs-b/PocketLedger.git
# cd PocketLedger
```

### 第四步：配置环境变量

```bash
# 创建 .env 文件
cat > .env << 'EOF'
# ========================================
# PocketLedger 环境配置
# ========================================

# 数据库配置 (重要：修改为你自己的强密码)
MYSQL_ROOT_PASSWORD=your_strong_root_password_here
MYSQL_USER=pocketledger
MYSQL_PASSWORD=your_strong_user_password_here
MYSQL_DATABASE=pocketledger

# 后端配置
SECRET_KEY=your-very-long-random-secret-key-at-least-32-characters
DATABASE_URL=mysql+pymysql://pocketledger:your_strong_user_password_here@db:3306/pocketledger
ACCESS_TOKEN_EXPIRE_MINUTES=10080
EOF
```

**重要提醒：**
- `MYSQL_ROOT_PASSWORD`: MySQL root 用户密码
- `MYSQL_PASSWORD`: pocketledger 用户密码
- `SECRET_KEY`: JWT 密钥，至少32位字符
- 建议使用强密码：随机生成或使用密码管理器

### 第五步：前端构建 (本地构建方式)

```bash
# 进入前端目录
cd frontend

# 安装 Node.js (如果未安装)
# curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
# sudo apt-get install -y nodejs

# 安装依赖
npm install

# 构建生产版本
npm run build

# 返回项目目录
cd ..

# 检查构建产物
ls -la frontend/dist/
```

### 第六步：Docker 部署 (后端 + 数据库)

```bash
# 启动数据库和后端
docker-compose up -d db backend

# 等待 MySQL 启动 (约10秒)
sleep 10

# 初始化数据库表
docker exec pocketledger-backend pip install pytz -q
docker exec pocketledger-backend python /code/backend/init_db.py

# 检查后端是否运行正常
curl http://localhost:8000/api/v1/health
# 应返回: {"status":"ok"}
```

### 第七步：Nginx 配置 (生产环境)

```bash
# 安装 Nginx
sudo apt install nginx -y

# 复制前端构建产物到 Nginx 目录
sudo cp -r frontend/dist/* /var/www/html/

# 创建 Nginx 配置文件
sudo cat > /etc/nginx/sites-available/pocketledger << 'EOF'
server {
    listen 80;
    server_name localhost;
    root /var/www/html;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # API 代理到后端
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }

    # Vue Router SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 启用配置
sudo ln -s /etc/nginx/sites-available/pocketledger /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 第八步：防火墙配置 (可选)

```bash
# 开放端口
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000

# 启用防火墙
sudo ufw enable
```

---

## ✅ 验证部署

```bash
# 1. 检查 Docker 服务状态
docker-compose ps

# 预期看到:
# pocketledger-db      mysql:8.0      Up
# pocketledger-backend uvicorn        Up

# 2. 测试后端 API 健康检查
curl http://localhost:8000/api/v1/health
# 返回: {"status":"ok"}

# 3. 测试后端 API 文档
浏览器访问: http://localhost:8000/docs

# 4. 测试前端页面
浏览器访问: http://localhost
```

---

## 🔑 首次使用流程

### 1. 注册第一个用户 (无需邀请码)

由于是第一个用户，系统会自动跳过邀请码验证：

```bash
# 使用 API 注册 (替换为你的信息)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "email": "your_email@example.com",
    "password": "your_password",
    "invitation_code": ""
  }'
```

**注意**: 第一个用户传空 `invitation_code` 即可

### 2. 登录获取 Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

**返回示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 3. 创建邀请码 (供其他用户注册)

```bash
# 复制上一步返回的 token
TOKEN="your_access_token_here"

# 创建邀请码
curl -X POST http://localhost:8000/api/v1/users/invitations \
  -H "Authorization: Bearer $TOKEN"
```

**返回示例**:
```json
{
  "id": 1,
  "code": "POCKET2024ABC123",
  "is_active": true,
  "max_uses": 10,
  "current_uses": 0,
  "created_at": "2026-02-06T15:00:00"
}
```

### 4. 其他用户注册

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user2",
    "email": "user2@example.com",
    "password": "password123",
    "invitation_code": "POCKET2024ABC123"
  }'
```

---

## 📝 常用管理命令

```bash
# 进入项目目录
cd /var/www/PocketLedger

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
docker-compose logs -f backend  # 只看后端日志
docker-compose logs -f db       # 只看数据库日志

# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart backend
docker-compose restart db

# 停止所有服务
docker-compose down

# 停止并删除数据卷 (慎用！会删除所有数据)
docker-compose down -v

# 更新代码后重新部署
git pull
cd frontend
npm run build
cd ..
docker-compose restart backend nginx

# 进入容器内部
docker exec -it pocketledger-backend bash
docker exec -it pocketledger-db mysql -u root -p
```

---

## 🐛 常见问题排查

### Q1: 后端返回 404 Not Found
```bash
# 检查后端容器是否运行
docker ps | grep backend

# 查看后端日志
docker-compose logs backend

# 重启后端
docker-compose restart backend
```

### Q2: 数据库连接失败
```bash
# 检查数据库容器
docker ps | grep db

# 查看数据库日志
docker-compose logs db

# 检查数据库连接
docker exec -it pocketledger-db mysql -u root -p
```

### Q3: 前端构建失败
```bash
# 清理并重新构建
cd frontend
rm -rf node_modules dist
npm install
npm run build
```

### Q4: Nginx 502 Bad Gateway
```bash
# 检查后端是否运行
curl http://localhost:8000/api/v1/health

# 重启 Nginx
sudo systemctl restart nginx

# 检查 Nginx 配置
sudo nginx -t
```

### Q5: 邀请码验证失败
```bash
# 登录后查看邀请码列表
curl -X GET http://localhost:8000/api/v1/users/invitations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔒 安全建议

1. **修改默认密码**: 确保 `.env` 中的密码足够强
2. **配置 SSL**: 生产环境建议使用 HTTPS
3. **限制 CORS**: 生产环境不要使用 `allow_origins=["*"]`
4. **定期备份**: 定期备份数据库
5. **监控日志**: 开启日志监控，及时发现问题

---

## 📞 获取帮助

- 项目地址: https://github.com/xrs-b/PocketLedger
- API 文档: http://your-server:8000/docs (部署后访问)
- 前端界面: http://your-server (部署后访问)

---

**部署完成！开始你的记账之旅吧！** 🎉
