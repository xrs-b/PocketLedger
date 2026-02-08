# 移动账本 - 完整系统设计

> 版本: 1.0  
> 生成时间: 2026-02-09  
> 状态: 待开发

---

## 一、项目概述

### 1.1 项目目标
开发一款移动端记账应用，支持日常记账和项目记账，提供多维度统计分析，部署在云服务器 VPS 上实现 7x24 小时运行。

### 1.2 核心特性
- ✅ 日常记账（随时记录，简洁快速）
- ✅ 项目记账（有时间范围，关联消费）
- ✅ 多维度统计（日常+项目交叉统计）
- ✅ 用户系统（邀请码注册，管理员）
- ✅ 二级分类（14个一级分类，覆盖日常消费）
- ✅ 移动端适配（完美适配手机）

---

## 二、功能需求

### 2.1 用户系统

#### 2.1.1 用户字段
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 账号名（唯一） |
| password_hash | VARCHAR(255) | 密码（加密） |
| is_admin | BOOLEAN | 是否管理员 |
| is_active | BOOLEAN | 是否有效 |
| created_at | DATETIME | 注册时间 |
| updated_at | DATETIME | 更新时间 |

#### 2.1.2 注册流程
```
1. 输入账号名
2. 输入密码
3. 输入邀请码 (vip1123)
4. 验证邀请码
5. 创建用户（is_admin = FALSE）
6. 注册成功提示
7. 2秒后自动跳转登录页
```

#### 2.1.3 首个管理员
- 第1个注册的用户自动设置 `is_admin = TRUE`
- 后续用户 `is_admin = FALSE`

#### 2.1.4 登录流程
```
1. 输入账号名/密码
2. 后端验证
3. 返回 JWT Token
4. 登录成功跳转首页
```

---

### 2.2 日常记账

#### 2.2.1 记账字段
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID |
| type | VARCHAR(10) | 收入/支出 |
| category_id | INTEGER | 一级分类ID |
| category_item_id | INTEGER | 二级分类ID |
| amount | DECIMAL(10,2) | 金额 |
| date | DATETIME | 日期时间 |
| remark | VARCHAR(255) | 备注 |
| payment_method_id | INTEGER | 支付方式 |
| project_id | INTEGER | 关联项目ID（可选） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 2.2.2 操作流程
```
1. 打开应用
2. 点击"记一笔"
3. 选择类型（收入/支出）
4. 选择分类（一级 → 二级）
5. 输入金额
6. 可选：备注、支付方式
7. 点击保存
8. 保存成功提示
9. 返回列表页
```

---

### 2.3 项目记账

#### 2.3.1 项目字段
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID（创建者） |
| title | VARCHAR(100) | 项目标题 |
| start_date | DATE | 开始日期 |
| end_date | DATE | 结束日期 |
| budget | DECIMAL(10,2) | 预算金额 |
| member_count | INTEGER | 参与人数 |
| total_expense | DECIMAL(10,2) | 已消费金额 |
| status | VARCHAR(20) | 进行中/已完成 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 2.3.2 人均计算
```python
人均费用 = total_expense / member_count
```

#### 2.3.3 项目记账流程
```
1. 项目列表页
2. 点击项目 → 进入详情页
3. 点击"记一笔"
4. 跳转记账界面（自动带项目标题）
5. 填写记账信息
6. 提交 → 记录关联到项目 + 显示在日常记账中
```

---

### 2.4 二级分类

#### 2.4.1 支出分类（10个一级分类）
| 一级分类 | 二级分类 |
|----------|----------|
| 餐饮 | 外卖/餐厅、食材杂货、饮料零食、下午茶/咖啡 |
| 交通 | 飞机、高铁、地铁/公交、打车/自驾、共享单车 |
| 购物 | 服装/鞋子、电子产品、日用品、化妆品、家居用品 |
| 娱乐 | 电影/演出、游戏/充值、旅游/门票、运动健身 |
| 住房 | 房租/房贷、水电费、物业费、装修材料 |
| 通讯 | 电话费、网络费 |
| 人情 | 送礼、红包/份子钱、聚会请客 |
| 医疗 | 药品、医院/诊所、保健品 |
| 教育 | 学费/培训费、书籍/资料、学习用品 |
| 其他 | 宠物、理财亏损、捐款、罚款、未知消费 |

#### 2.4.2 收入分类（4个一级分类）
| 一级分类 | 二级分类 |
|----------|----------|
| 工资 | 固定工资、奖金/提成、加班费 |
| 副业 | 兼职、自由职业、卖二手 |
| 投资 | 股票收益、基金收益、利息收入 |
| 其他 | 红包收入、退款、报销、意外之财 |

#### 2.4.3 支付方式
| 支付方式 |
|----------|
| 现金 |
| 银行卡 |
| 支付宝 |
| 微信 |
| 信用卡 |
| 电子钱包 |

---

### 2.5 统计报表

#### 2.5.1 筛选条件
| 条件 | 说明 |
|------|------|
| 日期范围 | 开始日期 + 结束日期（具体到日） |
| 分类 | 默认全部分类，可选一级/二级 |
| 数据来源 | 日常记账 + 项目关联记账（交叉统计） |

#### 2.5.2 统计维度
| 维度 | 说明 |
|------|------|
| 时间维度 | 按日/周/月/年汇总 |
| 类型维度 | 收入/支出/净收入 |
| 分类维度 | 一级分类汇总、二级分类明细、占比 |
| 项目维度 | 项目关联消费、非项目消费 |
| 支付维度 | 各支付方式统计 |
| 对比分析 | 环比（vs上月）、同比（vs去年） |

#### 2.5.3 可视化图表
| 图表类型 | 说明 |
|----------|------|
| 收支趋势折线图 | 时间范围内的收支变化 |
| 分类占比饼图 | 各分类占比 |
| 收支对比柱状图 | 收入 vs 支出 |

---

### 2.6 后端管理

#### 2.6.1 访问控制
- 路径: `/admin`
- 只有 `is_admin = TRUE` 的用户可访问

#### 2.6.2 管理功能
| 功能 | CRUD |
|------|------|
| 用户管理 | 查看、编辑、删除 |
| 记账列表 | 查看、编辑、删除 |
| 分类管理 | 查看、新增、编辑、删除 |
| 项目列表 | 查看、编辑、删除 |

---

## 三、技术架构

### 3.1 前端
| 技术 | 版本 |
|------|------|
| Vue | 3.x |
| Vite | 5.x |
| Element Plus | 2.x (移动端适配) |
| Pinia | 2.x |
| ECharts | 5.x |
| Axios | 1.x |

### 3.2 后端
| 技术 | 版本 |
|------|------|
| Python | 3.12 |
| FastAPI | 0.115.x |
| SQLAlchemy | 2.0.x |
| Pydantic | 2.5.x |
| JWT | - |

### 3.3 数据库
| 技术 | 选择 |
|------|------|
| SQLite | ✅ 轻量、无需额外服务 |
| MySQL | ❌ 需要额外服务 |

**选择**: SQLite（简化部署）

### 3.4 部署架构
```
┌─────────────────────────────────────────────┐
│              Nginx (80/443)                 │
├─────────────────────────────────────────────┤
│        前端 (静态文件 - Vite 构建)           │
├─────────────────────────────────────────────┤
│        后端 API (FastAPI)                   │
├─────────────────────────────────────────────┤
│        数据库 (SQLite)                       │
└─────────────────────────────────────────────┘
```

### 3.5 Docker 部署
```yaml
version: '3.8'

services:
  app:
    build: .
    ports: ["8000:8000"]
    volumes:
      - ./app:/code
      - ./data:/data
    command: uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 四、数据库设计

### 4.1 ER 图
```
users ───< records ───< category_items
  │          │
  └──< projects ───< category_items
  │
  └──< categories
  │
  └──< payment_methods
```

### 4.2 数据表
| 表名 | 说明 |
|------|------|
| users | 用户表 |
| categories | 一级分类表 |
| category_items | 二级分类表 |
| payment_methods | 支付方式表 |
| records | 记账记录表 |
| projects | 项目表 |

### 4.3 索引设计
```sql
-- records 表索引
CREATE INDEX idx_records_user_id ON records(user_id);
CREATE INDEX idx_records_date ON records(date);
CREATE INDEX idx_records_category ON records(category_id);
CREATE INDEX idx_records_project ON records(project_id);

-- projects 表索引
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_date ON projects(start_date, end_date);
```

---

## 五、API 设计

### 5.1 认证模块
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/register | 注册 |
| POST | /api/v1/auth/login | 登录 |
| POST | /api/v1/auth/logout | 登出 |
| GET | /api/v1/auth/me | 获取当前用户 |

### 5.2 记账模块
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/records | 记账列表 |
| POST | /api/v1/records | 创建记录 |
| GET | /api/v1/records/{id} | 记录详情 |
| PUT | /api/v1/records/{id} | 更新记录 |
| DELETE | /api/v1/records/{id} | 删除记录 |

### 5.3 项目模块
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/projects | 项目列表 |
| POST | /api/v1/projects | 创建项目 |
| GET | /api/v1/projects/{id} | 项目详情 |
| PUT | /api/v1/projects/{id} | 更新项目 |
| DELETE | /api/v1/projects/{id} | 删除项目 |

### 5.4 统计模块
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/statistics/summary | 汇总统计 |
| GET | /api/v1/statistics/by-category | 分类统计 |
| GET | /api/v1/statistics/by-project | 项目统计 |
| GET | /api/v1/statistics/trend | 趋势分析 |

### 5.5 分类模块
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/categories | 分类列表 |
| GET | /api/v1/categories/items | 二级分类列表 |
| GET | /api/v1/payment-methods | 支付方式列表 |

### 5.6 管理模块 (需管理员)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/admin/users | 用户列表 |
| PUT | /api/v1/admin/users/{id} | 更新用户 |
| DELETE | /api/v1/admin/users/{id} | 删除用户 |
| GET | /api/v1/admin/records | 所有记录 |
| DELETE | /api/v1/admin/records/{id} | 删除记录 |
| GET | /api/v1/admin/categories | 分类管理 |
| POST | /api/v1/admin/categories | 新增分类 |
| PUT | /api/v1/admin/categories/{id} | 更新分类 |
| DELETE | /api/v1/admin/categories/{id} | 删除分类 |

---

## 六、用户体验设计

### 6.1 移动端适配
- ✅ 禁止横向滚动
- ✅ 完美适配手机屏幕
- ✅ 响应式设计

### 6.2 设计风格
- ✅ 有设计感（阴影、圆角、渐变）
- ✅ 层次分明
- ✅ 色彩搭配舒适

### 6.3 交互规范
| 规范 | 说明 |
|------|------|
| 边距 | 页面边距 16px |
| 按钮 | 主按钮 ≥ 48px × 120px |
| 提示 | 成功/失败/加载都有 Toast 提示 |
| 返回 | 二级页面左上角返回按钮 |

### 6.4 导航结构
```
┌─────────────────────────────────────┐
│ 🏠 首页                              │
├─────────────────────────────────────┤
│ 📊 统计                              │
├─────────────────────────────────────┤
│ 📝 记一笔                            │
├─────────────────────────────────────┤
│ 📂 项目                              │
├─────────────────────────────────────┤
│ 👤 我的                              │
└─────────────────────────────────────┘
```

---

## 七、部署方案

### 7.1 服务器要求
| 配置 | 要求 |
|------|------|
| CPU | 1 核 |
| 内存 | 1GB |
| 磁盘 | 10GB |
| 系统 | Ubuntu 22.04 LTS |

### 7.2 Docker 一键部署
```bash
# 一键部署
curl -s https://raw.githubusercontent.com/xrs-b/mobile-ledger/main/deploy.sh | bash
```

### 7.3 域名配置
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /var/www/mobile-ledger/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
    }
}
```

### 7.4 HTTPS 配置 (Let's Encrypt)
```bash
certbot --nginx -d your-domain.com
```

---

## 八、开发计划

### Phase 1: 基础框架
- [ ] 项目初始化
- [ ] 数据库设计
- [ ] 用户认证 (注册/登录)
- [ ] 基础 CRUD 框架

### Phase 2: 核心功能
- [ ] 日常记账 CRUD
- [ ] 二级分类
- [ ] 项目记账
- [ ] 统计报表

### Phase 3: 管理后台
- [ ] 管理员认证
- [ ] 用户管理
- [ ] 数据管理

### Phase 4: 部署优化
- [ ] Docker 部署
- [ ] 域名配置
- [ ] HTTPS
- [ ] 备份恢复

---

## 九、参考项目

- PocketLedger: https://github.com/xrs-b/PocketLedger
- 钱迹: https://sspai.com/post/61668
- ezBookkeeping: https://zhuanlan.zhihu.com/p/1939683852458099780

---

*文档版本: 1.0*
*最后更新: 2026-02-09*
