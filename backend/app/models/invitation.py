from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timedelta
import pytz

shanghai_tz = pytz.timezone("Asia/Shanghai")


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    max_uses = Column(Integer, default=1)  # 最大使用次数
    used_count = Column(Integer, default=0)  # 已使用次数
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(shanghai_tz))
    expires_at = Column(DateTime, nullable=True)

    # 关系
    created_by = relationship("User", back_populates="invitations")

    @property
    def can_use(self) -> bool:
        """检查邀请码是否还能使用"""
        if not self.is_active:
            return False
        # 确保使用 aware datetime 进行比较
        now = datetime.now(shanghai_tz)
        if self.expires_at:
            expires_at = self.expires_at
            if expires_at.tzinfo is None:
                expires_at = shanghai_tz.localize(expires_at)
            if now > expires_at:
                return False
        return self.used_count < self.max_uses

    def use(self) -> None:
        """使用邀请码"""
        if self.can_use:
            self.used_count += 1

    def __repr__(self):
        return f"<Invitation {self.code}>"


from app.models.user import User
