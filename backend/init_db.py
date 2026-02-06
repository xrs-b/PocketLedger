#!/usr/bin/env python3
"""初始化 PocketLedger 数据库表"""

import sys
import os

# 添加 backend 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models import user, category, record, project, budget, invitation


def init_db():
    """创建所有数据库表"""
    print("正在创建数据库表...")
    
    try:
        # 创建表
        user.User.metadata.create_all(bind=engine)
        print("✓ User 表")
        
        category.Category.metadata.create_all(bind=engine)
        print("✓ Category 表")
        
        record.Record.metadata.create_all(bind=engine)
        print("✓ Record 表")
        
        project.Project.metadata.create_all(bind=engine)
        print("✓ Project 表")
        
        budget.Budget.metadata.create_all(bind=engine)
        print("✓ Budget 表")
        
        invitation.Invitation.metadata.create_all(bind=engine)
        print("✓ Invitation 表")
        
        print("\n✅ 数据库初始化完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        print("\n可能的解决方案:")
        print("1. 确保 MySQL 容器正在运行: docker ps | grep mysql")
        print("2. 确保数据库已创建: CREATE DATABASE IF NOT EXISTS pocketledger;")
        print("3. 检查 .env 文件中的数据库配置是否正确")
        return False


if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)
