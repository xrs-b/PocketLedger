#!/bin/bash
# PocketLedger 一键部署脚本
# 支持 Ubuntu 22.04/24.04

set -e

echo "======================================"
echo "  PocketLedger 一键部署脚本"
echo "======================================"
echo ""

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}请使用 root 用户运行！${NC}"
    exit 1
fi

# 步骤 1: 安装 Docker
echo -e "${YELLOW}[1/6] 安装 Docker...${NC}"
if ! command -v docker &> /dev/null; then
    apt-get update
    apt-get install -y curl wget git
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sh /tmp/get-docker.sh
    usermod -aG docker $USER
    rm /tmp/get-docker.sh
    echo -e "${GREEN}✓ Docker 安装完成${NC}"
else
    echo -e "${GREEN}✓ Docker 已安装${NC}"
fi

# 步骤 2: 安装 Docker Compose
echo -e "${YELLOW}[2/6] 安装 Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    apt-get install -y docker-compose
    echo -e "${GREEN}✓ Docker Compose 安装完成${NC}"
else
    echo -e "${GREEN}✓ Docker Compose 已安装${NC}"
fi

# 步骤 3: 克隆项目
echo -e "${YELLOW}[3/6] 克隆项目...${NC}"
if [ -d "/var/www/PocketLedger" ]; then
    echo "项目已存在，更新中..."
    cd /var/www/PocketLedger
    git pull
else
    mkdir -p /var/www
    cd /var/www
    git clone https://github.com/xrs-b/PocketLedger.git
    cd PocketLedger
fi
echo -e "${GREEN}✓ 项目准备完成${NC}"

# 步骤 4: 配置环境
echo -e "${YELLOW}[4/6] 配置环境变量...${NC}"
cd /var/www/PocketLedger
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ .env 文件已创建${NC}"
else
    echo -e "${GREEN}✓ .env 文件已存在${NC}"
fi

# 步骤 5: 部署
echo -e "${YELLOW}[5/6] 部署服务...${NC}"
docker-compose down --volumes --rmi all 2>/dev/null || true
docker system prune -af --volumes 2>/dev/null || true
docker-compose up -d --build
echo -e "${GREEN}✓ 服务启动中 (等待 30 秒)...${NC}"
sleep 30

# 步骤 6: 初始化数据库
echo -e "${YELLOW}[6/6] 初始化数据库...${NC}"
docker exec pocketledger-backend pip install pytz -q 2>/dev/null || true
docker exec pocketledger-backend python /code/backend/init_db.py

# 验证
echo ""
echo "======================================"
echo -e "${GREEN}部署完成！${NC}"
echo "======================================"
echo ""
echo "验证命令:"
echo "  - 后端健康检查: curl http://localhost:8000/api/v1/health"
echo "  - 前端页面: curl http://localhost"
echo ""
echo "管理命令:"
echo "  - 查看状态: cd /var/www/PocketLedger && docker-compose ps"
echo "  - 查看日志: cd /var/www/PocketLedger && docker-compose logs -f"
echo "  - 重启服务: cd /var/www/PocketLedger && docker-compose restart"
echo "  - 停止服务: cd /var/www/PocketLedger && docker-compose down"
echo ""
