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
def auth_headers(test_user, client):
    """获取认证后的请求头"""
    login_resp = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_profile_success(client, test_user, auth_headers):
    """测试获取个人资料（已登录）"""
    response = client.get(
        "/api/v1/users/profile",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"


def test_update_profile_success(client, test_user, auth_headers):
    """测试更新个人资料"""
    response = client.put(
        "/api/v1/users/profile",
        headers=auth_headers,
        json={
            "username": "updateduser",
            "email": "updated@example.com"
        }
    )
    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"
    assert response.json()["email"] == "updated@example.com"


def test_update_username(client, test_user, auth_headers):
    """测试更新用户名"""
    response = client.put(
        "/api/v1/users/profile",
        headers=auth_headers,
        json={
            "username": "newusername"
        }
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newusername"


def test_update_email(client, test_user, auth_headers):
    """测试更新邮箱"""
    response = client.put(
        "/api/v1/users/profile",
        headers=auth_headers,
        json={
            "email": "newemail@example.com"
        }
    )
    assert response.status_code == 200
    assert response.json()["email"] == "newemail@example.com"


def test_get_invitations(client, test_user, auth_headers, db_session):
    """测试获取邀请码列表"""
    # 先创建一个邀请码
    invitation = Invitation(
        code="TESTINVITE",
        max_uses=5,
        created_by_id=test_user.id
    )
    db_session.add(invitation)
    db_session.commit()
    
    response = client.get(
        "/api/v1/users/invitations",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["code"] == "TESTINVITE"
    assert response.json()[0]["max_uses"] == 5


def test_create_invitation(client, test_user, auth_headers):
    """测试创建邀请码"""
    response = client.post(
        "/api/v1/users/invitations",
        headers=auth_headers,
        json={}
    )
    assert response.status_code == 201
    assert "code" in response.json()
    assert len(response.json()["code"]) == 8
    assert response.json()["max_uses"] == 1  # 默认值


def test_create_invitation_with_custom_max_uses(client, test_user, auth_headers):
    """测试自定义最大使用次数创建邀请码"""
    response = client.post(
        "/api/v1/users/invitations",
        headers=auth_headers,
        json={
            "max_uses": 10
        }
    )
    assert response.status_code == 201
    assert "code" in response.json()
    assert len(response.json()["code"]) == 8
    assert response.json()["max_uses"] == 10


def test_get_profile_without_token(client):
    """测试无 token 访问被拒绝"""
    response = client.get("/api/v1/users/profile")
    assert response.status_code == 401
