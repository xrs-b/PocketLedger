from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import pytz
import enum

shanghai_tz = pytz.timezone("Asia/Shanghai")


class BudgetPeriod(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class AlertType(str, enum.Enum):
    WARNING = "warning"  # 接近预算
    OVER = "over"  # 超出预算


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    amount = Column(Integer, nullable=False)  # 预算金额（分）
    period = Column(SQLEnum(BudgetPeriod), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)  # 可选：按分类预算
    alert_threshold = Column(Integer, default=80)  # 预警百分比（默认80%）
    is_active = Column(Boolean, default=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(shanghai_tz))
    updated_at = Column(DateTime, default=lambda: datetime.now(shanghai_tz), onupdate=lambda: datetime.now(shanghai_tz))

    # 外键
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 关系
    user = relationship("User", back_populates="budgets")
    category = relationship("Category")

    def __repr__(self):
        return f"<Budget {self.name}: {self.amount}>"
