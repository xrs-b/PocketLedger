# PocketLedger Ubuntu 部署教程

> 基于 Ubuntu 22.04/24.04 LTS

---

## 环境要求

- **系统:** Ubuntu 22.04 LTS 或 24.04 LTS
- **内存:** 最低 1GB (推荐 2GB+)
- **磁盘:** 最低 10GB 可用空间
- **网络:** 可访问互联网

---

## 第一步：更新系统

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 第二步：安装 Docker

### 方式一：一键安装 (推荐)

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 方式二：手动安装

```bash
# 安装依赖
sudo apt install -y curl wget gnupg lsb-release

# 添加 Docker 官方 GPG 密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 添加 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 验证安装

```bash
docker --version
docker compose version
```

---

## 第三步：克隆项目

```bash
# 创建项目目录
mkdir -p /var/www
cd /var/www

# 克隆项目
git clone https://github.com/xrs-b/PocketLedger.git
cd PocketLedger
```

---

## 第四步：配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置 (必填: SECRET_KEY)
nano .env
```

### .env 文件配置说明

```bash
# 数据库配置 (按需修改)
MYSQL_ROOT_PASSWORD=rootpassword      # MySQL root 密码
MYSQL_USER=pocketledger               # 应用用户名
MYSQL_PASSWORD=password               # 应用密码
MYSQL_DATABASE=pocketledger           # 数据库名

# 后端配置 (必须修改!)
SECRET_KEY=your-very-long-random-secret-key-at-least-32-characters-here
# ⚠️ 重要: 生成一个强密码，例如:
# SECRET_KEY=$(openssl rand -base64 32)

ACCESS_TOKEN_EXPIRE_MINUTES=10080     # Token 过期时间 (7天)
```

### 生成安全的 SECRET_KEY

```bash
# 方法 1: 使用 openssl (推荐)
openssl rand -base64 32

# 方法 2: 使用 python
python3 -c "import secrets; print(secrets.token_hex(32))"

# 方法 3: 使用 uuid
uuidgen | md5sum
```

---

## 第五步：部署服务

### 一键部署 (推荐)

```bash
# 给予执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

### 手动部署

```bash
# 1. 停止旧服务 (如果存在)
docker-compose down --volumes --rmi all 2>/dev/null || true

# 2. 清理 Docker 缓存 (可选)
docker system prune -af --volumes 2>/dev/null || true

# 3. 构建并启动所有服务
docker-compose up -d --build

# 4. 等待服务启动
echo "等待服务启动..."
sleep 30

# 5. 检查服务状态
docker-compose ps
```

---

## 第六步：验证部署

### 1. 检查容器状态

```bash
docker-compose ps
```

预期输出:
```
NAME                 STATUS    PORTS
pocketledger-backend  Up       0.0.0.0:8000->8000/tcp
pocketledger-db      Up       0.0.0.0:3306->3306/tcp
pocketledger-frontend Up       0.0.0.0:80->80/tcp
```

### 2. 测试后端健康检查

```bash
curl -s http://localhost:8000/health
```

预期输出:
```json
{"status":"ok"}
```

### 3. 测试登录接口 (JSON 格式)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test"}'
```

预期输出 (用户不存在时):
```json
{"detail":"用户不存在"}
```

### 4. 测试前端页面

```bash
# 访问首页
curl -s http://localhost | head -20

# 或者用浏览器访问
# http://你的服务器IP
```

---

## 常用管理命令

### 查看状态

```bash
# 查看所有容器状态
docker-compose ps

# 查看容器资源使用
docker stats
```

### 查看日志

```bash
# 查看所有日志
docker-compose logs -f

# 只看后端日志
docker-compose logs -f backend

# 只看最近 50 行
docker-compose logs --tail=50
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart backend
docker-compose restart frontend
docker-compose restart db
```

### 停止服务

```bash
# 停止所有服务 (保留数据)
docker-compose down

# 停止并删除数据卷 (⚠️ 删除所有数据!)
docker-compose down -v
```

### 完全重建

```bash
docker-compose down --volumes --rmi all
docker-compose up -d --build
```

---

## 故障排除

### 问题 1: Docker 命令需要 sudo

```bash
# 当前用户加入 docker 组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker
```

### 问题 2: 端口被占用

```bash
# 查看端口占用
sudo lsof -i :80
sudo lsof -i :8000
sudo lsof -i :3306

# 修改端口 (编辑 docker-compose.yml)
```

### 问题 3: 数据库连接失败

```bash
# 检查 MySQL 日志
docker logs pocketledger-db --tail 30

# 测试 MySQL 连接
docker exec pocketledger-db mysql -u root -prootpassword -e "SHOW DATABASES"
```

### 问题 4: 后端 404

```bash
# 检查后端日志
docker logs pocketledger-backend --tail 30

# 确保后端已启动
curl http://localhost:8000/health
```

### 问题 5: 前端页面无法访问

```bash
# 检查 Nginx 日志
docker logs pocketledger-frontend --tail 30

# 检查 Nginx 配置
docker exec pocketledger-frontend cat /etc/nginx/conf.d/default.conf
```

### 问题 6: 忘记 MySQL 密码

```bash
# 重置 MySQL 密码
docker-compose down -v
docker-compose up -d db
sleep 10

# 进入 MySQL 容器
docker exec -it pocketledger-db mysql -u root -prootpassword

# 在 MySQL 中执行
# ALTER USER 'root'@'%' IDENTIFIED BY '新密码';
```

---

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://你的服务器IP | Web 应用 |
| 后端 API | http://你的服务器IP:8000 | API 服务 |
| API 文档 | http://你的服务器IP:8000/docs | Swagger UI |
| 健康检查 | http://你的服务器IP:8000/health | 后端状态 |

---

## 安全加固 (生产环境)

### 1. 修改默认密码

编辑 `.env` 文件:

```bash
MYSQL_ROOT_PASSWORD=你的强密码
MYSQL_PASSWORD=你的强密码
SECRET_KEY=你的强密钥 (至少 32 字符)
```

### 2. 配置防火墙

```bash
# 允许 SSH (22端口)
sudo ufw allow 22

# 允许 HTTP (80端口)
sudo ufw allow 80

# 允许 HTTPS (443端口, 如需)
sudo ufw allow 443

# 启用防火墙
sudo ufw enable
```

### 3. 配置 SSL/HTTPS (可选)

使用 Let's Encrypt:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d 你的域名
```

---

## 数据备份

### 备份数据库

```bash
# 创建备份目录
mkdir -p /backup

# 备份命令
docker exec pocketledger-db mysqldump -u root -prootpassword pocketledger > /backup/pocketledger_$(date +%Y%m%d).sql
```

### 自动备份脚本

```bash
#!/bin/bash
# /backup/backup.sh

BACKUP_DIR=/backup
DATE=$(date +%Y%m%d_%H%M%S)
docker exec pocketledger-db mysqldump -u root -prootpassword pocketledger > $BACKUP_DIR/pocketledger_$DATE.sql

# 删除 7 天前的备份
find $BACKUP_DIR -name "pocketledger_*.sql" -mtime +7 -delete

echo "Backup completed: pocketledger_$DATE.sql"
```

添加定时任务:

```bash
crontab -e

# 添加每天凌晨 3 点备份
0 3 * * * /backup/backup.sh >> /var/log/backup.log 2>&1
```

---

## 卸载清理

```bash
# 停止并删除所有容器和数据卷
docker-compose down -v --rmi all

# 删除项目目录
sudo rm -rf /var/www/PocketLedger

# 删除备份目录 (如有)
sudo rm -rf /backup
```

---

## 技术支持

如果遇到问题:

1. 查看日志: `docker-compose logs -f`
2. 检查文档: `docs/ARCHITECTURE_ANALYSIS.md`
3. 提交 Issue: https://github.com/xrs-b/PocketLedger/issues

---

*更新时间: 2026-02-07*
