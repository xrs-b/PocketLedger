# PocketLedger 部署指南

## 快速部署 (Docker)

### 1. 克隆项目
```bash
git clone https://github.com/xrs-b/PocketLedger.git
cd PocketLedger
```

### 2. 配置环境变量
```bash
# 复制环境变量文件
cp .env.example .env

# 编辑配置 (可选)
nano .env
```

### 3. 一键部署
```bash
chmod +x deploy.sh
./deploy.sh
```

### 4. 验证
```bash
# 测试后端健康检查
curl http://localhost:8000/health

# 测试前端
curl http://localhost
```

---

## 手动部署步骤

### 步骤 1: 安装 Docker
```bash
# Ubuntu
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 步骤 2: 安装 Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 步骤 3: 部署
```bash
# 克隆项目
git clone https://github.com/xrs-b/PocketLedger.git
cd PocketLedger

# 配置环境
cp .env.example .env

# 构建并启动
docker-compose up -d --build

# 等待启动
sleep 30

# 检查状态
docker-compose ps
```

### 步骤 4: 初始化数据库 (如果需要)
```bash
docker exec pocketledger-backend python /code/backend/init_db.py
```

---

## 本地开发部署

### 环境要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0

### 1. 启动 MySQL (Docker)
```bash
docker run -d \
  --name mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=pocketledger \
  mysql:8.0
```

### 2. 启动后端
```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动 (热重载)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 启动前端
```bash
cd frontend

# 安装依赖
npm install

# 开发模式 (热重载)
npm run dev
```

---

## API 端点

### 健康检查
- `GET /health` - 后端健康状态

### 认证
- `POST /api/v1/auth/register` - 用户注册 (需要邀请码)
- `POST /api/v1/auth/login` - 用户登录 (JSON: `{email, password}`)
- `POST /api/v1/auth/logout` - 用户登出
- `GET /api/v1/auth/me` - 获取当前用户信息
- `POST /api/v1/auth/refresh` - 刷新令牌

### 用户
- `GET /api/v1/users/profile` - 获取用户资料
- `PUT /api/v1/users/profile` - 更新用户资料
- `GET /api/v1/users/invitations` - 获取邀请码列表
- `POST /api/v1/users/invitations` - 创建邀请码

### 分类
- `GET /api/v1/categories` - 获取分类列表
- `POST /api/v1/categories` - 创建分类
- `PUT /api/v1/categories/{id}` - 更新分类
- `DELETE /api/v1/categories/{id}` - 删除分类
- `GET /api/v1/categories/items` - 获取预设分类
- `GET /api/v1/categories/presets` - 获取预设分类

### 记录
- `GET /api/v1/records` - 获取记账记录列表
- `POST /api/v1/records` - 创建记账记录
- `GET /api/v1/records/{id}` - 获取记录详情
- `PUT /api/v1/records/{id}` - 更新记录
- `DELETE /api/v1/records/{id}` - 删除记录

### 项目
- `GET /api/v1/projects` - 获取项目列表
- `POST /api/v1/projects` - 创建项目
- `GET /api/v1/projects/{id}` - 获取项目详情
- `PUT /api/v1/projects/{id}` - 更新项目
- `DELETE /api/v1/projects/{id}` - 删除项目
- `GET /api/v1/projects/{id}/stats` - 获取项目统计

### 预算
- `GET /api/v1/budgets` - 获取预算列表
- `POST /api/v1/budgets` - 创建预算
- `GET /api/v1/budgets/{id}` - 获取预算详情
- `PUT /api/v1/budgets/{id}` - 更新预算
- `DELETE /api/v1/budgets/{id}` - 删除预算
- `GET /api/v1/budgets/alerts` - 获取预算提醒

### 统计
- `GET /api/v1/statistics/monthly` - 月度统计
- `GET /api/v1/statistics/range` - 范围统计
- `GET /api/v1/statistics/categories` - 分类统计
- `GET /api/v1/statistics/projects` - 项目统计
- `GET /api/v1/statistics/overview` - 概览统计

---

## 故障排除

### 问题 1: 后端 404
```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查后端日志
docker logs pocketledger-backend --tail 50
```

### 问题 2: 数据库连接失败
```bash
# 检查 MySQL 状态
docker ps | grep mysql

# 检查 MySQL 日志
docker logs pocketledger-db --tail 50

# 测试 MySQL 连接
docker exec pocketledger-db mysql -u root -prootpassword -e "SHOW DATABASES"
```

### 问题 3: 前端 404
```bash
# 检查前端容器
docker ps | grep frontend

# 检查 Nginx 配置
docker exec pocketledger-frontend cat /etc/nginx/conf.d/default.conf

# 重启前端
docker restart pocketledger-frontend
```

### 问题 4: 端口被占用
```bash
# 查看端口占用
lsof -i :8000
lsof -i :80

# 停止占用端口的进程
kill <PID>
```

---

## 常用命令

```bash
# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
docker-compose logs -f backend  # 只看后端

# 重启服务
docker-compose restart
docker-compose restart backend  # 只重启后端

# 停止服务
docker-compose down

# 停止并删除数据卷 (慎用！)
docker-compose down -v

# 完全重建
docker-compose down --volumes --rmi all
docker-compose up -d --build
```
