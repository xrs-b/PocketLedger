#!/usr/bin/env python3
"""初始化 PocketLedger 数据库表"""

import sys
import os

# 添加 backend 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from app.models.user import User
from app.models.category import Category
from app.models.record import Record
from app.models.project import Project
from app.models.budget import Budget
from app.models.invitation import Invitation


def init_db():
    """创建所有数据库表"""
    print("正在创建数据库表...")
    
    # 导入所有模型
    from app.models import user, category, record, project, budget, invitation
    
    # 创建表
    User.metadata.create_all(bind=engine)
    print("✓ User 表")
    
    Category.metadata.create_all(bind=engine)
    print("✓ Category 表")
    
    Record.metadata.create_all(bind=engine)
    print("✓ Record 表")
    
    Project.metadata.create_all(bind=engine)
    print("✓ Project 表")
    
    Budget.metadata.create_all(bind=engine)
    print("✓ Budget 表")
    
    Invitation.metadata.create_all(bind=engine)
    print("✓ Invitation 表")
    
    print("\n✅ 数据库初始化完成！")


if __name__ == "__main__":
    init_db()
