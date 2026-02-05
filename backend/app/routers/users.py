import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.invitation import Invitation
from app.auth.jwt import get_current_user
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.invitation import InvitationResponse, CreateInvitationRequest

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的个人资料"""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前登录用户的个人资料"""
    # 检查用户名是否被其他用户使用
    if user_update.username and user_update.username != current_user.username:
        existing_user = db.query(User).filter(User.username == user_update.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被使用"
            )
        current_user.username = user_update.username
    
    # 检查邮箱是否被其他用户使用
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
        current_user.email = user_update.email
    
    # 更新 is_active 状态
    if user_update.is_active is not None:
        current_user.is_active = user_update.is_active
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/invitations", response_model=list[InvitationResponse])
async def get_user_invitations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户创建的所有邀请码"""
    invitations = db.query(Invitation).filter(Invitation.created_by_id == current_user.id).all()
    return invitations


@router.post("/invitations", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    request: CreateInvitationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的邀请码"""
    # 生成邀请码 (8位随机字符串)
    code = secrets.token_urlsafe(6)[:8].upper()
    
    invitation = Invitation(
        code=code,
        max_uses=request.max_uses,
        created_by_id=current_user.id
    )
    
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    return invitation
