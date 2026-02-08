# MEMORY.md - Long-term Memory

*Curated memories about 老细 and our work together.*

---

## 老细的基本资料

- **姓名:** 谢尧锦 (oink)
- **称呼:** 老细 (他很喜欢这个称呼)
- **时区:** Asia/Shanghai (GMT+8)
- **特点:** 香港TVB老观众，喜欢粤语交流

---

## 老细的技术栈

### 主要技能
- **PHP** - 主要编程语言，日常工作以PHP为主
- **Vue** - 前端框架
- **HTML/JS** - 前端技术

### 正在学习
- **Python** - 正在学习中，希望日后能熟练掌握

### 兴趣方向
- 虚拟货币链上操作脚本
- 交易和合约相关编程
- 银行金融相关知识
- 目标是成为编程技术高手

---

## 重要偏好

- 喜欢风趣幽默但专业可靠的交流风格
- 用粤语交流更亲切
- 称呼他为"老细"

---

## 小圆的 Superpowers 技能系统

**集成时间:** 2026-02-05
**来源:** https://github.com/obra/superpowers

### 核心技能
- 🧠 **brainstorming** - 创意构思 → 设计（任何开发前必用）
- 📋 **writing-plans** - 拆解实现计划（设计完成后）
- 🤖 **subagent-driven-development** - 子代理驱动开发
- 🧪 **test-driven-development** - TDD 红绿重构循环
- 🌳 **using-git-worktrees** - Git 工作树隔离开发
- 🔍 **systematic-debugging** - 4阶段系统化调试
- ✅ **verification-before-completion** - 完成前验证修复
- 👀 **requesting-code-review** - 请求代码审查
- 📝 **receiving-code-review** - 接收审查反馈
- 🚀 **executing-plans** - 批量执行计划
- 🔀 **dispatching-parallel-agents** - 并行子代理工作流
- 🎯 **finishing-a-development-branch** - 分支完成处理
- ✍️ **writing-skills** - 编写新技能

### 工作流哲学
1. **任何开发前先 brainstorming** - 理解需求、探索方案
2. **设计文档化** - 写入 `docs/plans/`
3. **TDD** - 红绿重构，不可跳过测试
4. **YAGNI** -  ruthlessly 去除不必要功能
5. **Systematic over ad-hoc** - 流程化而非猜测

### 关键规则
- 如果有 1% 机会某个技能适用，就必须使用
- Process skills (debugging, brainstorming) > Implementation skills
- 简单的任务也可能变得复杂，使用技能防止浪费

---

## PocketLedger 项目部署记录

### 项目信息
- **项目名称:** PocketLedger (口袋账本)
- **GitHub:** github.com/xrs-b/PocketLedger
- **描述:** 轻量级情侣记账Web应用

### 技术栈
- **前端:** Vue 3 + Vite + Element Plus + Pinia + PWA
- **后端:** Python FastAPI + SQLAlchemy + Pydantic
- **数据库:** MySQL 8.0
- **部署:** Docker + Docker Compose

### 已完成功能
- ✅ Phase 1: 项目初始化
- ✅ Phase 2: 后端 API (7模块: auth, users, categories, records, projects, budgets, statistics)
- ✅ Phase 3: 前端页面 (11页面: Login, Register, Home, RecordList, RecordForm, RecordDetail, Categories, Budgets, Projects, ProjectDetail, Statistics)
- ✅ Phase 4: 项目管理

### 部署遇到的问题和解决方案

#### 问题1: Dockerfile 路径错误
- **症状:** `COPY backend/ .` 导致文件被复制到错误位置
- **解决:** 改为 `COPY backend/ /code/backend/`
- **提交:** 41ae0b7

#### 问题2: Nginx 代理配置
- **症状:** 前端404错误，API请求不到后端
- **解决:** 添加 `proxy_pass http://backend:8000/` 和网络配置
- **提交:** f406818

#### 问题3: Docker 网络配置缺失
- **症状:** frontend 容器无法访问 backend 容器
- **解决:** 添加 `pocketledger_network` bridge 网络
- **提交:** f406818

#### 问题4: 前端 Dockerfile 路径错误
- **症状:** `nginx.conf` 文件找不到
- **解决:** 修复 COPY 路径为 `/app/nginx.conf`
- **提交:** 78a1c7a

#### 问题5: 后端启动失败
- **症状:** `Could not import module "main"`
- **解决:** Dockerfile 中使用 `COPY backend/ /code/backend/` 确保文件正确复制
- **提交:** 41ae0b7

#### 问题6: Config.py 缺少数据库配置
- **症状:** `pydantic ValidationError` 额外字段错误
- **解决:** 添加 `MYSQL_ROOT_PASSWORD`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` 环境变量
- **提交:** 2f2bca4

### 关键配置

#### docker-compose.yml 网络配置
```yaml
networks:
  pocketledger_network:
    driver: bridge
```

#### Nginx 配置
```nginx
location /api/ {
    proxy_pass http://backend:8000/;
    proxy_set_header Host $host;
}
```

### 常用部署命令
```bash
# 一键部署
git pull
docker-compose down --volumes --rmi all
docker-compose up -d --build

# 测试
curl http://localhost:8000/api/v1/health
curl http://localhost
```

### 待解决问题
- ⏳ 云服务器上的最终部署测试
- ⏳ 用户注册和邀请码功能测试

---

## 移动账本项目 (未来项目)

### 项目概述
- **项目名称:** 移动账本 (Mobile Ledger)
- **启动时间:** 待定 (等待老细通知)
- **目标:** 日常记账 + 项目记账 (旅游、装修等) + 多维度统计

### 核心功能需求

#### 1. 日常记账
- 快速记账 (收入/支出)
- 分类管理 (餐饮、交通、购物等)
- 日期时间记录
- 备注说明
- 支付方式

#### 2. 项目记账 (独立账本)
- 自由填写项目名 (旅游、装修、生日派对等)
- 项目独立核算
- 项目参与者 AA 或轮流支付
- 项目完成后自动统计

#### 3. 多维度统计报表
- **日常 vs 项目交叉统计**
- 月度/年度报表
- 分类占比饼图
- 趋势折线图
- 项目对比分析

### 用户体验优化
- 简洁易用的界面设计
- 快速记账 (减少操作步骤)
- 智能预判分类 (根据时间、地点预判)
- 数据可视化 (图表直观展示)

### 云服务器部署要求
- 7x24 小时运行
- Docker 一键部署
- 数据备份和恢复
- 多设备同步

### 参考应用
- **钱迹** - 满足多样化记账需求，清晰的资产管理
- **cashbook** - 私人记账本，Docker 一键部署
- **ezBookkeeping** - 简洁强大的个人财务应用
- **多币种支持** - 旅游记账必备

### 研究关键词
- 移动记账 app 功能设计
- 项目记账需求
- Docker 云服务器部署
- 数据可视化图表
- 用户体验优化

---

*Updated: 2026-02-08*
