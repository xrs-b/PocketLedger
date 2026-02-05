import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.invitation import Invitation
from app.auth.password import get_password_hash
from app.auth.jwt import create_access_token

# 设置测试环境
os.environ["TESTING"] = "1"


# 测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """获取认证头"""
    token = create_access_token(data={"sub": test_user.id, "username": test_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_invitation(db_session, test_user):
    """创建测试邀请码"""
    invitation = Invitation(
        code="TEST1234",
        max_uses=3,
        created_by_id=test_user.id
    )
    db_session.add(invitation)
    db_session.commit()
    db_session.refresh(invitation)
    return invitation


class TestUserProfile:
    """测试用户个人资料相关接口"""
    
    def test_get_profile_success(self, client, test_user, auth_headers):
        """测试获取个人资料成功"""
        response = client.get("/api/v1/users/profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["is_active"] == test_user.is_active
        assert data["is_verified"] == test_user.is_verified
        assert "created_at" in data
    
    def test_get_profile_without_token(self, client):
        """测试无令牌获取个人资料"""
        response = client.get("/api/v1/users/profile")
        assert response.status_code == 401
    
    def test_update_profile_success(self, client, test_user, auth_headers):
        """测试更新个人资料成功"""
        response = client.put(
            "/api/v1/users/profile",
            headers=auth_headers,
            json={"username": "newusername", "email": "newemail@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newusername"
        assert data["email"] == "newemail@example.com"
    
    def test_update_profile_partial(self, client, test_user, auth_headers):
        """测试部分更新个人资料"""
        response = client.put(
            "/api/v1/users/profile",
            headers=auth_headers,
            json={"username": "partialupdate"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "partialupdate"
        # 邮箱应保持不变
        assert data["email"] == test_user.email


class TestUserInvitations:
    """测试用户邀请码相关接口"""
    
    def test_get_invitations_success(self, client, test_user, test_invitation, auth_headers):
        """测试获取邀请码列表成功"""
        response = client.get("/api/v1/users/invitations", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["code"] == test_invitation.code
        assert data[0]["max_uses"] == test_invitation.max_uses
    
    def test_get_invitations_empty(self, client, test_user, auth_headers):
        """测试无邀请码时返回空列表"""
        response = client.get("/api/v1/users/invitations", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []
    
    def test_create_invitation_success(self, client, test_user, auth_headers):
        """测试创建邀请码成功"""
        response = client.post(
            "/api/v1/users/invitations",
            headers=auth_headers,
            json={"max_uses": 5}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["code"] is not None
        assert len(data["code"]) == 8
        assert data["max_uses"] == 5
        assert data["used_count"] == 0
        assert data["is_active"] == True
    
    def test_create_invitation_default_max_uses(self, client, test_user, auth_headers):
        """测试创建邀请码使用默认最大使用次数"""
        response = client.post(
            "/api/v1/users/invitations",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["max_uses"] == 1  # 默认值
    
    def test_get_invitations_without_token(self, client):
        """测试无令牌获取邀请码列表"""
        response = client.get("/api/v1/users/invitations")
        assert response.status_code == 401
    
    def test_create_invitation_without_token(self, client):
        """测试无令牌创建邀请码"""
        response = client.post("/api/v1/users/invitations", json={"max_uses": 5})
        assert response.status_code == 401
