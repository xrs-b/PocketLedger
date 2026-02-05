from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import pytz
import enum

shanghai_tz = pytz.timezone("Asia/Shanghai")


class RecordType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    WECHAT = "wechat"
    ALIPAY = "alipay"
    BANK_CARD = "bank_card"
    OTHER = "other"


class SplitMethod(str, enum.Enum):
    EQUAL = "equal"  # 均分
    EXACT = "exact"  # 精确分摊
    PERCENTAGE = "percentage"  # 按比例
    SHARE = "share"  # 多人分摊


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(RecordType), nullable=False)
    amount = Column(Integer, nullable=False)  # 金额（分）
    description = Column(String(200), nullable=True)
    note = Column(Text, nullable=True)  # 详细备注
    
    # 多人相关字段
    payer_count = Column(Integer, default=1)  # 付款人数
    total_people = Column(Integer, default=1)  # 总人数（包含非付款人）
    split_amount = Column(Integer, nullable=True)  # 每人分摊金额
    
    payment_method = Column(SQLEnum(PaymentMethod), nullable=True)
    date = Column(DateTime, nullable=False)  # 消费日期
    created_at = Column(DateTime, default=lambda: datetime.now(shanghai_tz))
    updated_at = Column(DateTime, default=lambda: datetime.now(shanghai_tz), onupdate=lambda: datetime.now(shanghai_tz))

    # 外键
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    # 关系
    user = relationship("User", back_populates="records")
    category = relationship("Category", back_populates="records")
    project = relationship("Project", back_populates="records")

    def __repr__(self):
        return f"<Record {self.amount} ({self.type})>"
