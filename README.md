# PocketLedger

轻量级情侣/个人记账 Web 应用

## 技术栈

- **前端**: Vue 3 + Vite + Element Plus + Pinia + TailwindCSS + PWA
- **后端**: Python FastAPI + SQLAlchemy + Pydantic
- **数据库**: MySQL 8.0
- **部署**: Docker + Docker Compose

## 功能特性

- 👤 用户认证 (JWT + 邀请码注册)
- 💰 日常收支记账 (支持 AA 制)
- 📁 项目型记账 (装修、旅游等)
- 💡 预算管理 (带超支提醒)
- 📊 多维度统计分析
- 🏷️ 二级分类管理

## 项目结构

```
PocketLedger/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── models/       # SQLAlchemy 数据模型
│   │   ├── routers/      # API 路由 (7个模块)
│   │   ├── schemas/      # Pydantic 模式
│   │   ├── auth/         # JWT 认证
│   │   ├── main.py       # 入口
│   │   └── database.py   # 数据库配置
│   ├── Dockerfile        # 后端 Docker 镜像
│   └── requirements.txt  # Python 依赖
│
├── frontend/             # Vue 3 前端
│   ├── src/
│   │   ├── views/        # 页面 (11个)
│   │   ├── components/   # 组件 (7个)
│   │   │   └── charts/   # ECharts 图表 (3个)
│   │   ├── api/          # API 调用层 (7个)
│   │   ├── stores/       # Pinia 状态管理
│   │   └── router/       # Vue Router 配置
│   ├── Dockerfile        # 前端 Docker 镜像
│   ├── nginx.conf        # Nginx 配置
│   └── package.json      # Node 依赖
│
├── docker-compose.yml    # Docker Compose 配置
└── README.md             # 项目说明
```

## 快速部署

### 环境要求

- Docker & Docker Compose
- Git

### 部署步骤

```bash
# 1. 克隆项目
git clone https://github.com/xrs-b/PocketLedger.git
cd PocketLedger

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 设置密码

# 3. 启动服务
docker-compose up -d --build

# 4. 验证部署
# 后端 API: http://localhost:8000/docs
# 前端页面: http://localhost
```

### 环境变量 (.env)

```env
# Database
MYSQL_ROOT_PASSWORD=your_strong_root_password
MYSQL_USER=pocketledger
MYSQL_PASSWORD=your_strong_user_password
MYSQL_DATABASE=pocketledger

# Backend
SECRET_KEY=your-very-long-random-secret-key
DATABASE_URL=mysql+pymysql://pocketledger:your_strong_user_password@db:3306/pocketledger
```

## 本地开发

### 后端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置 .env 文件
cp .env.example .env

# 启动 MySQL (Docker)
docker-compose up -d db

# 初始化数据库
alembic upgrade head

# 启动后端
uvicorn main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## API 文档

启动后端服务后，访问: http://localhost:8000/docs

## 许可证

MIT License
