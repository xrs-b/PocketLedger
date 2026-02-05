from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import pytz
import enum

shanghai_tz = pytz.timezone("Asia/Shanghai")


class CategoryType(str, enum.Enum):
    INCOME = "income"  # 收入
    EXPENSE = "expense"  # 支出


class CategoryLevel(str, enum.Enum):
    PRIMARY = "primary"  # 一级分类
    SECONDARY = "secondary"  # 二级分类


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    type = Column(SQLEnum(CategoryType), nullable=False)
    level = Column(SQLEnum(CategoryLevel), default=CategoryLevel.PRIMARY)
    icon = Column(String(50), nullable=True)  # 图标标识
    color = Column(String(20), nullable=True)  # 颜色代码
    sort_order = Column(Integer, default=0)  # 排序
    is_system = Column(Boolean, default=False)  # 是否系统预设
    is_active = Column(Boolean, default=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(shanghai_tz))
    updated_at = Column(DateTime, default=lambda: datetime.now(shanghai_tz), onupdate=lambda: datetime.now(shanghai_tz))

    # 关系
    user = relationship("User", back_populates="categories")
    parent = relationship("Category", remote_side=[id], backref="children")
    records = relationship("Record", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name} ({self.type})>"
