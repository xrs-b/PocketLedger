from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timedelta
import pytz
import secrets

shanghai_tz = pytz.timezone("Asia/Shanghai")


class InvitationCode(Base):
    __tablename__ = "invitation_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    max_uses = Column(Integer, default=1)  # 最大使用次数
    current_uses = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(shanghai_tz))

    # 外键
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 关系
    created_by = relationship("User", back_populates="invitation_codes")

    @classmethod
    def generate_code(cls) -> str:
        """生成邀请码"""
        return secrets.token_urlsafe(8)[:10].upper()

    @property
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return datetime.now(shanghai_tz) > self.expires_at

    @property
    def can_use(self) -> bool:
        """检查是否可以使用"""
        return (
            self.is_active
            and not self.is_expired
            and self.current_uses < self.max_uses
        )

    def use(self) -> bool:
        """使用邀请码"""
        if not self.can_use:
            return False
        self.current_uses += 1
        return True

    def __repr__(self):
        return f"<InvitationCode {self.code}>"
