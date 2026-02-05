import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.invitation import InvitationCode
from app.auth.password import get_password_hash

# 测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session):
    """创建异步测试客户端"""
    app.dependency_overrides[get_db] = lambda: db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_register_success(async_client, db_session):
    """测试注册成功"""
    # 先创建邀请码
    creator = User(
        username="creator",
        email="creator@example.com",
        hashed_password=get_password_hash("password")
    )
    db_session.add(creator)
    await db_session.commit()
    
    invitation = InvitationCode(
        code="TEST1234",
        max_uses=3,
        created_by_id=creator.id
    )
    db_session.add(invitation)
    await db_session.commit()
    
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpassword123",
            "invitation_code": "TEST1234"
        }
    )
    assert response.status_code == 201
    assert response.json()["message"] == "注册成功"


@pytest.mark.asyncio
async def test_register_invalid_invitation_code(async_client):
    """测试无效邀请码"""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpassword123",
            "invitation_code": "INVALID"
        }
    )
    assert response.status_code == 400
    assert "邀请码" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(async_client, db_session):
    """测试登录成功"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(user)
    await db_session.commit()
    
    response = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(async_client, db_session):
    """测试密码错误"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(user)
    await db_session.commit()
    
    response = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(async_client, db_session):
    """测试获取当前用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(user)
    await db_session.commit()
    
    # 先登录获取 token
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    
    # 获取当前用户
    response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_current_user_without_token(async_client):
    """测试无令牌获取用户"""
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(async_client, db_session):
    """测试登出"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(user)
    await db_session.commit()
    
    # 先登录
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    
    # 登出
    response = await async_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "message" in response.json()
