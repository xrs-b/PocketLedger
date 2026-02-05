from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class InvitationResponse(BaseModel):
    """邀请码响应模型"""
    id: int
    code: str
    max_uses: int
    used_count: int
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CreateInvitationRequest(BaseModel):
    """创建邀请码请求模型"""
    max_uses: int = 1  # 默认只能使用一次
