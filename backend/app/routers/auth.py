from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.invitation import Invitation
from app.auth.jwt import create_access_token, get_current_user
from app.auth.password import verify_password
from app.schemas.auth import Token, LoginRequest, RegisterRequest, MessageResponse
from app.schemas.user import UserCreate, UserResponse


class LoginForm(BaseModel):
    """JSON 登录请求格式 - 替代 OAuth2PasswordRequestForm"""
    email: EmailStr
    password: str

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册（需要邀请码）"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已注册
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 验证邀请码
    invitation = db.query(Invitation).filter(
        Invitation.code == request.invitation_code,
        Invitation.is_active == True
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请码无效"
        )
    
    # 检查是否过期
    from datetime import datetime
    import pytz
    shanghai_tz = pytz.timezone("Asia/Shanghai")
    if invitation.expires_at and datetime.now(shanghai_tz) > invitation.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请码已过期"
        )
    
    if not invitation.can_use:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邀请码已失效"
        )
    
    # 创建用户
    from app.auth.password import get_password_hash
    user = User(
        username=request.username,
        email=request.email,
        hashed_password=get_password_hash(request.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 使用邀请码
    invitation.use()
    db.commit()
    
    return {"message": "注册成功"}


@router.post("/login", response_model=Token)
async def login(
    request: LoginForm,  # ← 使用 JSON 格式
    db: Session = Depends(get_db)
):
    """用户登录 (JSON 格式)"""
    # 通过 email 查找用户
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出（客户端删除令牌即可）"""
    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token: str = Depends(OAuth2PasswordRequestForm),
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    from app.auth.jwt import decode_token
    
    payload = decode_token(token)
    user_id: int = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
