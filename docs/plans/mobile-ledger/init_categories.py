#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移动账本 - 数据库初始化脚本
生成默认分类和支付方式数据
"""

import sqlite3
import os

DB_PATH = "pocketledger.db"

def init_database():
    """初始化数据库表结构"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建一级分类表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL UNIQUE,
            type VARCHAR(10) NOT NULL,
            icon VARCHAR(50),
            sort_order INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建二级分类表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS category_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name VARCHAR(50) NOT NULL,
            icon VARCHAR(50),
            sort_order INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        )
    ''')
    
    # 创建支付方式表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL UNIQUE,
            icon VARCHAR(50),
            sort_order INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    return conn


def seed_categories(cursor):
    """插入一级分类"""
    
    # 支出分类
    expense_categories = [
        ('餐饮', 'food', 1),
        ('交通', 'transport', 2),
        ('购物', 'shopping', 3),
        ('娱乐', 'entertainment', 4),
        ('住房', 'housing', 5),
        ('通讯', 'communication', 6),
        ('人情', 'social', 7),
        ('医疗', 'medical', 8),
        ('教育', 'education', 9),
        ('其他', 'other', 10),
    ]
    
    # 收入分类
    income_categories = [
        ('工资', 'salary', 1),
        ('副业', 'side_hustle', 2),
        ('投资', 'investment', 3),
        ('其他', 'other', 4),
    ]
    
    # 插入支出分类
    for name, icon, sort_order in expense_categories:
        cursor.execute('''
            INSERT OR IGNORE INTO categories (name, type, icon, sort_order)
            VALUES (?, 'expense', ?, ?)
        ''', (name, icon, sort_order))
    
    # 插入收入分类
    for name, icon, sort_order in income_categories:
        cursor.execute('''
            INSERT OR IGNORE INTO categories (name, type, icon, sort_order)
            VALUES (?, 'income', ?, ?)
        ''', (name, icon, sort_order))


def seed_category_items(cursor):
    """插入二级分类"""
    
    category_items = {
        # 餐饮 (category_id=1)
        '餐饮': [
            ('外卖/餐厅', 1),
            ('食材杂货', 2),
            ('饮料零食', 3),
            ('下午茶/咖啡', 4),
        ],
        # 交通 (category_id=2)
        '交通': [
            ('飞机', 1),
            ('高铁', 2),
            ('地铁/公交', 3),
            ('打车/自驾', 4),
            ('共享单车', 5),
        ],
        # 购物 (category_id=3)
        '购物': [
            ('服装/鞋子', 1),
            ('电子产品', 2),
            ('日用品', 3),
            ('化妆品', 4),
            ('家居用品', 5),
        ],
        # 娱乐 (category_id=4)
        '娱乐': [
            ('电影/演出', 1),
            ('游戏/充值', 2),
            ('旅游/门票', 3),
            ('运动健身', 4),
        ],
        # 住房 (category_id=5)
        '住房': [
            ('房租/房贷', 1),
            ('水电费', 2),
            ('物业费', 3),
            ('装修材料', 4),
        ],
        # 通讯 (category_id=6)
        '通讯': [
            ('电话费', 1),
            ('网络费', 2),
        ],
        # 人情 (category_id=7)
        '人情': [
            ('送礼', 1),
            ('红包/份子钱', 2),
            ('聚会请客', 3),
        ],
        # 医疗 (category_id=8)
        '医疗': [
            ('药品', 1),
            ('医院/诊所', 2),
            ('保健品', 3),
        ],
        # 教育 (category_id=9)
        '教育': [
            ('学费/培训费', 1),
            ('书籍/资料', 2),
            ('学习用品', 3),
        ],
        # 其他 (category_id=10)
        '其他': [
            ('宠物', 1),
            ('理财亏损', 2),
            ('捐款', 3),
            ('罚款', 4),
            ('未知消费', 5),
        ],
        # 工资 (category_id=11)
        '工资': [
            ('固定工资', 1),
            ('奖金/提成', 2),
            ('加班费', 3),
        ],
        # 副业 (category_id=12)
        '副业': [
            ('兼职', 1),
            ('自由职业', 2),
            ('卖二手', 3),
        ],
        # 投资 (category_id=13)
        '投资': [
            ('股票收益', 1),
            ('基金收益', 2),
            ('利息收入', 3),
        ],
        # 其他收入 (category_id=14)
        '其他': [
            ('红包收入', 1),
            ('退款', 2),
            ('报销', 3),
            ('意外之财', 4),
        ],
    }
    
    for category_name, items in category_items.items():
        # 获取分类ID
        cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
        result = cursor.fetchone()
        if result:
            category_id = result[0]
            for item_name, sort_order in items:
                cursor.execute('''
                    INSERT OR IGNORE INTO category_items (category_id, name, sort_order)
                    VALUES (?, ?, ?)
                ''', (category_id, item_name, sort_order))


def seed_payment_methods(cursor):
    """插入支付方式"""
    
    payment_methods = [
        ('现金', 'cash', 1),
        ('银行卡', 'card', 2),
        ('支付宝', 'alipay', 3),
        ('微信', 'wechat', 4),
        ('信用卡', 'credit_card', 5),
        ('电子钱包', 'e_wallet', 6),
    ]
    
    for name, icon, sort_order in payment_methods:
        cursor.execute('''
            INSERT OR IGNORE INTO payment_methods (name, icon, sort_order)
            VALUES (?, ?, ?)
        ''', (name, icon, sort_order))


def main():
    """主函数"""
    
    print("=" * 50)
    print("  移动账本 - 数据库初始化")
    print("=" * 50)
    print()
    
    # 删除旧数据库
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️  已删除旧数据库: {DB_PATH}")
    
    # 初始化数据库
    conn = init_database()
    cursor = conn.cursor()
    print("✅ 数据库表结构已创建")
    
    # 插入数据
    print()
    print("📊 正在插入默认分类数据...")
    
    seed_categories(cursor)
    print("  ✅ 一级分类插入完成")
    
    seed_category_items(cursor)
    print("  ✅ 二级分类插入完成")
    
    seed_payment_methods(cursor)
    print("  ✅ 支付方式插入完成")
    
    # 提交并关闭
    conn.commit()
    
    # 统计
    cursor.execute("SELECT COUNT(*) FROM categories")
    cat_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM category_items")
    item_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM payment_methods")
    pm_count = cursor.fetchone()[0]
    
    print()
    print("=" * 50)
    print(f"  ✅ 初始化完成!")
    print()
    print(f"  📂 一级分类: {cat_count} 个")
    print(f"  📝 二级分类: {item_count} 个")
    print(f"  💳 支付方式: {pm_count} 个")
    print()
    print(f"  📁 数据库文件: {DB_PATH}")
    print("=" * 50)
    
    conn.close()


if __name__ == "__main__":
    main()
