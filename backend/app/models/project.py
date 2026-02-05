from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import pytz

shanghai_tz = pytz.timezone("Asia/Shanghai")


class ProjectStatus:
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    budget = Column(Float, nullable=True)
    status = Column(String(20), default=ProjectStatus.ACTIVE)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(shanghai_tz))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(shanghai_tz))

    # 关系
    owner = relationship("User", foreign_keys=[owner_id], back_populates="projects")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_projects")
    records = relationship("Record", back_populates="project", cascade="all, delete-orphan")

    def total_expenses(self) -> float:
        """计算项目总支出"""
        return sum(record.amount for record in self.records if record.type.value == "expense")

    def total_income(self) -> float:
        """计算项目总收入"""
        return sum(record.amount for record in self.records if record.type.value == "income")

    def balance(self) -> float:
        """计算项目结余"""
        return self.total_income() - self.total_expenses()

    def __repr__(self):
        return f"<Project {self.name}>"
