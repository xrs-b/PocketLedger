# 移动账本 - 二级分类设计

> 版本: 1.0
> 生成时间: 2026-02-08

---

## 一、分类设计原则

### 1.1 设计目标
- **全覆盖**：涵盖日常消费 95% 以上场景
- **无重叠**：分类之间不重复
- **易理解**：名称清晰易懂
- **可扩展**：支持自定义添加

### 1.2 结构说明
```
一级分类 → 二级分类
例如：
餐饮 → 外卖/餐厅、食材杂货、饮料零食
交通 → 飞机、高铁、地铁/公交、打车/自驾
```

---

## 二、支出分类

### 2.1 餐饮 (Food)
| 一级 | 二级分类 |
|------|----------|
| **餐饮** | 外卖/餐厅 |
| | 食材杂货 (自己煮饭材料) |
| | 饮料零食 (奶茶、甜品) |
| | 下午茶/咖啡 |

### 2.2 交通 (Transport)
| 一级 | 二级分类 |
|------|----------|
| **交通** | 飞机 |
| | 高铁 |
| | 地铁/公交 |
| | 打车/自驾 (含油费、过路费) |
| | 共享单车 |

### 2.3 购物 (Shopping)
| 一级 | 二级分类 |
|------|----------|
| **购物** | 服装/鞋子 |
| | 电子产品 |
| | 日用品 (洗漱用品、纸巾等) |
| | 化妆品 |
| | 家居用品 |

### 2.4 娱乐 (Entertainment)
| 一级 | 二级分类 |
|------|----------|
| **娱乐** | 电影/演出 |
| | 游戏/充值 |
| | 旅游/门票 |
| | 运动健身 |

### 2.5 住房 (Housing)
| 一级 | 二级分类 |
|------|----------|
| **住房** | 房租/房贷 |
| | 水电费 |
| | 物业费 |
| | 装修材料 |

### 2.6 通讯 (Communication)
| 一级 | 二级分类 |
|------|----------|
| **通讯** | 电话费 |
| | 网络费 |

### 2.7 人情 (Social)
| 一级 | 二级分类 |
|------|----------|
| **人情** | 送礼 |
| | 红包/份子钱 |
| | 聚会请客 |

### 2.8 医疗 (Medical)
| 一级 | 二级分类 |
|------|----------|
| **医疗** | 药品 |
| | 医院/诊所 |
| | 保健品 |

### 2.9 教育 (Education)
| 一级 | 二级分类 |
|------|----------|
| **教育** | 学费/培训费 |
| | 书籍/资料 |
| | 学习用品 |

### 2.10 其他 (Other)
| 一级 | 二级分类 |
|------|----------|
| **其他** | 宠物 |
| | 理财亏损 |
| | 捐款 |
| | 罚款 |
| | 未知消费 |

---

## 三、收入分类

### 3.1 职业收入
| 一级 | 二级分类 |
|------|----------|
| **工资** | 固定工资 |
| | 奖金/提成 |
| | 加班费 |

### 3.2 副业收入
| 一级 | 二级分类 |
|------|----------|
| **副业** | 兼职 |
| | 自由职业 |
| | 卖二手 |

### 3.3 投资收入
| 一级 | 二级分类 |
|------|----------|
| **投资** | 股票收益 |
| | 基金收益 |
| | 利息收入 |

### 3.4 其他收入
| 一级 | 二级分类 |
|------|----------|
| **其他** | 红包收入 |
| | 退款 |
| | 报销 |
| | 意外之财 |

---

## 四、支付方式 (独立维度)

| 支付方式 |
|----------|
| 现金 |
| 银行卡 |
| 支付宝 |
| 微信 |
| 信用卡 |
| 电子钱包 |

---

## 五、数据表设计

### 5.1 一级分类表 (categories)
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    type VARCHAR(10) NOT NULL,  -- 'expense' 或 'income'
    icon VARCHAR(50),           -- 图标名称
    sort_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 二级分类表 (category_items)
```sql
CREATE TABLE category_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);
```

### 5.3 支付方式表 (payment_methods)
```sql
CREATE TABLE payment_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 六、默认数据

### 6.1 一级分类
```sql
-- 支出分类
INSERT INTO categories (name, type, icon, sort_order) VALUES
('餐饮', 'expense', 'food', 1),
('交通', 'expense', 'transport', 2),
('购物', 'expense', 'shopping', 3),
('娱乐', 'expense', 'entertainment', 4),
('住房', 'expense', 'housing', 5),
('通讯', 'expense', 'communication', 6),
('人情', 'expense', 'social', 7),
('医疗', 'expense', 'medical', 8),
('教育', 'expense', 'education', 9),
('其他', 'expense', 'other', 10);

-- 收入分类
INSERT INTO categories (name, type, icon, sort_order) VALUES
('工资', 'income', 'salary', 1),
('副业', 'income', 'side_hustle', 2),
('投资', 'income', 'investment', 3),
('其他', 'income', 'other', 4);
```

### 6.2 二级分类
```sql
-- 餐饮
INSERT INTO category_items (category_id, name, sort_order) VALUES
(1, '外卖/餐厅', 1),
(1, '食材杂货', 2),
(1, '饮料零食', 3),
(1, '下午茶/咖啡', 4);

-- 交通
INSERT INTO category_items (category_id, name, sort_order) VALUES
(2, '飞机', 1),
(2, '高铁', 2),
(2, '地铁/公交', 3),
(2, '打车/自驾', 4),
(2, '共享单车', 5);

-- 购物
INSERT INTO category_items (category_id, name, sort_order) VALUES
(3, '服装/鞋子', 1),
(3, '电子产品', 2),
(3, '日用品', 3),
(3, '化妆品', 4),
(3, '家居用品', 5);

-- 娱乐
INSERT INTO category_items (category_id, name, sort_order) VALUES
(4, '电影/演出', 1),
(4, '游戏/充值', 2),
(4, '旅游/门票', 3),
(4, '运动健身', 4);

-- 住房
INSERT INTO category_items (category_id, name, sort_order) VALUES
(5, '房租/房贷', 1),
(5, '水电费', 2),
(5, '物业费', 3),
(5, '装修材料', 4);

-- 通讯
INSERT INTO category_items (category_id, name, sort_order) VALUES
(6, '电话费', 1),
(6, '网络费', 2);

-- 人情
INSERT INTO category_items (category_id, name, sort_order) VALUES
(7, '送礼', 1),
(7, '红包/份子钱', 2),
(7, '聚会请客', 3);

-- 医疗
INSERT INTO category_items (category_id, name, sort_order) VALUES
(8, '药品', 1),
(8, '医院/诊所', 2),
(8, '保健品', 3);

-- 教育
INSERT INTO category_items (category_id, name, sort_order) VALUES
(9, '学费/培训费', 1),
(9, '书籍/资料', 2),
(9, '学习用品', 3);

-- 其他
INSERT INTO category_items (category_id, name, sort_order) VALUES
(10, '宠物', 1),
(10, '理财亏损', 2),
(10, '捐款', 3),
(10, '罚款', 4),
(10, '未知消费', 5);

-- 工资
INSERT INTO category_items (category_id, name, sort_order) VALUES
(11, '固定工资', 1),
(11, '奖金/提成', 2),
(11, '加班费', 3);

-- 副业
INSERT INTO category_items (category_id, name, sort_order) VALUES
(12, '兼职', 1),
(12, '自由职业', 2),
(12, '卖二手', 3);

-- 投资
INSERT INTO category_items (category_id, name, sort_order) VALUES
(13, '股票收益', 1),
(13, '基金收益', 2),
(13, '利息收入', 3);

-- 其他收入
INSERT INTO category_items (category_id, name, sort_order) VALUES
(14, '红包收入', 1),
(14, '退款', 2),
(14, '报销', 3),
(14, '意外之财', 4);
```

### 6.3 支付方式
```sql
INSERT INTO payment_methods (name, icon, sort_order) VALUES
('现金', 'cash', 1),
('银行卡', 'card', 2),
('支付宝', 'alipay', 3),
('微信', 'wechat', 4),
('信用卡', 'credit_card', 5),
('电子钱包', 'e_wallet', 6);
```

---

## 七、分类统计展示

### 7.1 饼图展示
- 每笔消费对应一个二级分类
- 统计时按二级分类聚合
- 支持展开查看一级分类汇总

### 7.2 趋势图
- 按日/周/月聚合
- 区分收入/支出
- 支持对比分析

---

## 八、用户体验优化

### 8.1 快速选择
- 最近使用的分类置顶
- 收藏常用分类
- 搜索分类

### 8.2 智能预判
根据时间预判分类：
- 早餐时间 → 默认"餐饮-外卖/餐厅"
- 午餐时间 → 默认"餐饮-外卖/餐厅"
- 晚餐时间 → 默认"餐饮-外卖/餐厅"
- 周末下午 → 默认"餐饮-下午茶/咖啡"

---

## 九、部署说明

### 9.1 初始化脚本
```bash
# 数据库初始化
python init_db.py

# 或手动执行
sqlite3 pocketledger.db < categories.sql
sqlite3 pocketledger.db < category_items.sql
sqlite3 pocketledger.db < payment_methods.sql
```

### 9.2 自定义分类
用户可以在应用内：
- 添加新分类
- 修改分类名称
- 删除分类
- 调整顺序

---

*文档版本: 1.0*
*最后更新: 2026-02-08*
