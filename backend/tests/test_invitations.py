import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db

# 导入所有模型以确保表能被创建
from app.models.user import User
from app.models.category import Category
from app.models.record import Record
from app.models.project import Project
from app.models.budget import Budget
from app.models.invitation import Invitation

# 使用内存 SQLite 进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()


@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.mark.asyncio
async def test_invitation_model_creation(test_db):
    """测试邀请模型创建"""
    from app.models.invitation import Invitation
    from app.models.user import User
    
    db = TestingSessionLocal()
    try:
        # 先创建用户
        user = User(
            username="invitation_test",
            email="invitation@example.com",
            hashed_password="hashed_password"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 创建邀请码
        invitation = Invitation(
            code="TEST123456",
            max_uses=5,
            created_by_id=user.id
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        assert invitation.id is not None
        assert invitation.code == "TEST123456"
        assert invitation.max_uses == 5
        assert invitation.used_count == 0
        assert invitation.created_by_id == user.id
        assert invitation.is_active is True
        assert invitation.created_at is not None
    finally:
        db.close()


@pytest.mark.asyncio
async def test_invitation_can_use(test_db):
    """测试邀请码是否还能使用"""
    from app.models.invitation import Invitation
    from app.models.user import User
    from datetime import datetime, timedelta
    import pytz
    
    db = TestingSessionLocal()
    try:
        user = User(
            username="canuse_test",
            email="canuse@example.com",
            hashed_password="hashed"
        )
        db.add(user)
        db.commit()
        
        # 创建一个未过期的邀请码
        invitation = Invitation(
            code="CANUSE001",
            max_uses=3,
            created_by_id=user.id
        )
        db.add(invitation)
        db.commit()
        
        # 应该可以使用
        assert invitation.can_use is True
        
        # 创建一个已过期的邀请码
        shanghai_tz = pytz.timezone("Asia/Shanghai")
        expired_invitation = Invitation(
            code="EXPIRED001",
            max_uses=3,
            created_by_id=user.id,
            expires_at=datetime.now(shanghai_tz) - timedelta(days=1)
        )
        db.add(expired_invitation)
        db.commit()
        
        assert expired_invitation.can_use is False
        
        # 创建一个已用完的邀请码
        used_invitation = Invitation(
            code="USED001",
            max_uses=2,
            used_count=2,
            created_by_id=user.id
        )
        db.add(used_invitation)
        db.commit()
        
        assert used_invitation.can_use is False
        
        # 创建一个未激活的邀请码
        inactive_invitation = Invitation(
            code="INACTIVE001",
            max_uses=3,
            is_active=False,
            created_by_id=user.id
        )
        db.add(inactive_invitation)
        db.commit()
        
        assert inactive_invitation.can_use is False
    finally:
        db.close()


@pytest.mark.asyncio
async def test_invitation_use(test_db):
    """测试使用邀请码"""
    from app.models.invitation import Invitation
    from app.models.user import User
    
    db = TestingSessionLocal()
    try:
        user = User(
            username="use_test",
            email="use@example.com",
            hashed_password="hashed"
        )
        db.add(user)
        db.commit()
        
        invitation = Invitation(
            code="USETEST01",
            max_uses=3,
            used_count=0,
            created_by_id=user.id
        )
        db.add(invitation)
        db.commit()
        
        # 第一次使用
        invitation.use()
        db.commit()
        assert invitation.used_count == 1
        
        # 第二次使用
        invitation.use()
        db.commit()
        assert invitation.used_count == 2
        
        # 第三次使用
        invitation.use()
        db.commit()
        assert invitation.used_count == 3
        
        # 尝试第四次使用（应该不能再使用）
        invitation.use()
        db.commit()
        assert invitation.used_count == 3  # 不应该增加
    finally:
        db.close()


@pytest.mark.asyncio
async def test_invitation_relationship(test_db):
    """测试邀请码与用户的关系"""
    from app.models.invitation import Invitation
    from app.models.user import User
    
    db = TestingSessionLocal()
    try:
        user = User(
            username="relation_test",
            email="relation@example.com",
            hashed_password="hashed"
        )
        db.add(user)
        db.commit()
        
        invitation = Invitation(
            code="RELATION01",
            max_uses=5,
            created_by_id=user.id
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        # 检查关系
        assert invitation.created_by is not None
        assert invitation.created_by.id == user.id
        assert invitation.created_by.username == "relation_test"
    finally:
        db.close()


@pytest.mark.asyncio
async def test_user_invitations_relationship(test_db):
    """测试用户与邀请码的反向关系"""
    from app.models.invitation import Invitation
    from app.models.user import User
    
    db = TestingSessionLocal()
    try:
        user = User(
            username="reverse_test",
            email="reverse@example.com",
            hashed_password="hashed"
        )
        db.add(user)
        db.commit()
        
        # 创建多个邀请码
        inv1 = Invitation(code="REV001", max_uses=3, created_by_id=user.id)
        inv2 = Invitation(code="REV002", max_uses=5, created_by_id=user.id)
        inv3 = Invitation(code="REV003", max_uses=1, created_by_id=user.id)
        db.add_all([inv1, inv2, inv3])
        db.commit()
        
        # 检查用户的反向关系
        assert hasattr(user, 'invitations')
        assert len(user.invitations) == 3
    finally:
        db.close()


@pytest.mark.asyncio
async def test_invitation_unique_code(test_db):
    """测试邀请码唯一性约束"""
    from app.models.invitation import Invitation
    from app.models.user import User
    from sqlalchemy.exc import IntegrityError
    
    db = TestingSessionLocal()
    try:
        user = User(
            username="unique_test",
            email="unique@example.com",
            hashed_password="hashed"
        )
        db.add(user)
        db.commit()
        
        # 创建第一个邀请码
        inv1 = Invitation(code="UNIQUECODE", max_uses=3, created_by_id=user.id)
        db.add(inv1)
        db.commit()
        
        # 尝试创建重复的邀请码
        inv2 = Invitation(code="UNIQUECODE", max_uses=5, created_by_id=user.id)
        db.add(inv2)
        
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
    finally:
        db.close()
