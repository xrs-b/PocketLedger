from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Date
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import pytz

shanghai_tz = pytz.timezone("Asia/Shanghai")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(20), nullable=True)  # 项目颜色标识
    is_active = Column(Boolean, default=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(shanghai_tz))
    updated_at = Column(DateTime, default=lambda: datetime.now(shanghai_tz), onupdate=lambda: datetime.now(shanghai_tz))

    # 外键
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 关系
    owner = relationship("User", back_populates="projects")
    records = relationship("Record", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.name}>"
