from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import pytz
import enum

shanghai_tz = pytz.timezone("Asia/Shanghai")


class BudgetPeriodType(str, enum.Enum):
    MONTHLY = "monthly"  # 按月
    YEARLY = "yearly"  # 按年


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    period_type = Column(SQLEnum(BudgetPeriodType), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(shanghai_tz))
    updated_at = Column(DateTime, default=lambda: datetime.now(shanghai_tz), onupdate=lambda: datetime.now(shanghai_tz))

    # 关系
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")

    def __repr__(self):
        return f"<Budget {self.name}>"
