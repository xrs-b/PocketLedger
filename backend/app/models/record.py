from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import pytz
import enum

shanghai_tz = pytz.timezone("Asia/Shanghai")


class RecordType(str, enum.Enum):
    INCOME = "income"  # 收入
    EXPENSE = "expense"  # 支出


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    amount = Column(Float, nullable=False)  # 金额
    type = Column(SQLEnum(RecordType), nullable=False)
    description = Column(String(200), nullable=True)  # 备注
    date = Column(DateTime, nullable=False)  # 记账日期
    payer_count = Column(Integer, default=1)  # 付款人数
    payer_per_share = Column(Float, nullable=True)  # 人均应付
    is_aa = Column(Boolean, default=False)  # AA制
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # 可选关联项目
    created_at = Column(DateTime, default=lambda: datetime.now(shanghai_tz))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(shanghai_tz))

    # 关系
    user = relationship("User", back_populates="records")
    category = relationship("Category", back_populates="records")
    project = relationship("Project", back_populates="records")

    def calculate_per_share(self) -> float:
        """计算人均分摊金额"""
        if self.is_aa and self.payer_count and self.payer_count > 0:
            return round(self.amount / self.payer_count, 2)
        return self.amount

    def is_income(self) -> bool:
        """是否收入"""
        return self.type == RecordType.INCOME

    def __repr__(self):
        return f"<Record {self.amount} ({self.type})>"
