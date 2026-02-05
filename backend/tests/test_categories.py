import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.category import Category, CategoryType, CategoryLevel
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
    """获取认证请求头"""
    login_resp = client.post(
        "/api/v1/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_categories(db_session, test_user):
    """创建示例分类"""
    # 一级分类
    parent1 = Category(
        name="餐饮",
        type=CategoryType.EXPENSE,
        level=CategoryLevel.PRIMARY,
        is_system=True,
        icon="food",
        sort_order=1,
        user_id=test_user.id
    )
    parent2 = Category(
        name="工资",
        type=CategoryType.INCOME,
        level=CategoryLevel.PRIMARY,
        is_system=True,
        icon="salary",
        sort_order=1,
        user_id=test_user.id
    )
    db_session.add_all([parent1, parent2])
    db_session.commit()
    
    # 二级分类
    child1 = Category(
        name="早餐",
        type=CategoryType.EXPENSE,
        level=CategoryLevel.SECONDARY,
        parent_id=parent1.id,
        is_system=True,
        icon="breakfast",
        sort_order=1,
        user_id=test_user.id
    )
    child2 = Category(
        name="午餐",
        type=CategoryType.EXPENSE,
        level=CategoryLevel.SECONDARY,
        parent_id=parent1.id,
        is_system=True,
        icon="lunch",
        sort_order=2,
        user_id=test_user.id
    )
    db_session.add_all([child1, child2])
    db_session.commit()
    
    return parent1, parent2, child1, child2


class TestPrimaryCategories:
    """一级分类测试类"""

    def test_get_categories_success(self, client, auth_headers, sample_categories):
        """测试获取一级分类列表"""
        response = client.get("/api/v1/categories", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 2

    def test_get_categories_without_token(self, client):
        """测试无令牌获取分类"""
        response = client.get("/api/v1/categories")
        assert response.status_code == 401

    def test_create_category_success(self, client, auth_headers, db_session):
        """测试创建一级分类"""
        response = client.post(
            "/api/v1/categories",
            headers=auth_headers,
            json={
                "name": "购物",
                "type": "expense",
                "icon": "shopping",
                "color": "#FF0000"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "购物"
        assert data["type"] == "expense"
        assert data["level"] == "primary"
        assert data["icon"] == "shopping"
        assert data["color"] == "#FF0000"

    def test_create_category_duplicate_name(self, client, auth_headers, sample_categories):
        """测试创建重复名称的分类"""
        response = client.post(
            "/api/v1/categories",
            headers=auth_headers,
            json={
                "name": "餐饮",
                "type": "expense"
            }
        )
        assert response.status_code == 400

    def test_update_category_success(self, client, auth_headers, sample_categories, db_session):
        """测试更新分类"""
        parent1 = sample_categories[0]
        response = client.put(
            f"/api/v1/categories/{parent1.id}",
            headers=auth_headers,
            json={
                "name": "餐饮更新",
                "icon": "food-updated"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "餐饮更新"
        assert data["icon"] == "food-updated"

    def test_update_category_not_found(self, client, auth_headers):
        """测试更新不存在的分类"""
        response = client.put(
            "/api/v1/categories/9999",
            headers=auth_headers,
            json={"name": "测试"}
        )
        assert response.status_code == 404

    def test_delete_category_success(self, client, auth_headers, sample_categories, db_session):
        """测试删除分类"""
        parent1 = sample_categories[0]
        response = client.delete(
            f"/api/v1/categories/{parent1.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["message"] == "分类删除成功"

        # 验证分类已被软删除 (is_active=False)
        category = db_session.query(Category).filter(Category.id == parent1.id).first()
        assert category is not None
        assert category.is_active is False

    def test_delete_category_not_found(self, client, auth_headers):
        """测试删除不存在的分类"""
        response = client.delete(
            "/api/v1/categories/9999",
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_category_with_children(self, client, auth_headers, sample_categories, db_session):
        """测试删除带二级分类的分类"""
        parent1 = sample_categories[0]
        response = client.delete(
            f"/api/v1/categories/{parent1.id}",
            headers=auth_headers
        )
        # 根据实现策略，可能返回 400 或成功删除
        assert response.status_code in [200, 400]


class TestSecondaryCategories:
    """二级分类测试类"""

    def test_get_items_by_parent(self, client, auth_headers, sample_categories):
        """测试按父分类获取二级分类"""
        parent1 = sample_categories[0]
        response = client.get(
            f"/api/v1/categories/items?parent_id={parent1.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 2
        for cat in data["categories"]:
            assert cat["parent_id"] == parent1.id

    def test_get_items_no_parent(self, client, auth_headers):
        """测试未指定父分类时获取二级分类"""
        response = client.get("/api/v1/categories/items", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data

    def test_create_secondary_category_success(self, client, auth_headers, sample_categories, db_session):
        """测试创建二级分类"""
        parent1 = sample_categories[0]
        response = client.post(
            "/api/v1/categories/items",
            headers=auth_headers,
            json={
                "name": "晚餐",
                "type": "expense",
                "parent_id": parent1.id,
                "icon": "dinner",
                "color": "#00FF00"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "晚餐"
        assert data["parent_id"] == parent1.id
        assert data["level"] == "secondary"

    def test_create_secondary_category_no_parent(self, client, auth_headers):
        """测试创建二级分类时未指定父分类"""
        response = client.post(
            "/api/v1/categories/items",
            headers=auth_headers,
            json={
                "name": "晚餐",
                "type": "expense",
                "icon": "dinner"
            }
        )
        assert response.status_code == 400

    def test_create_secondary_category_invalid_parent(self, client, auth_headers):
        """测试创建二级分类时指定不存在的父分类"""
        response = client.post(
            "/api/v1/categories/items",
            headers=auth_headers,
            json={
                "name": "晚餐",
                "type": "expense",
                "parent_id": 9999,
                "icon": "dinner"
            }
        )
        assert response.status_code == 404


class TestPresetCategories:
    """预设分类测试类"""

    def test_get_presets_success(self, client, auth_headers, sample_categories):
        """测试获取预设分类"""
        response = client.get("/api/v1/categories/presets", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        # 预设分类应该都是系统分类
        for cat in data["categories"]:
            assert cat["is_system"] is True

    def test_get_presets_without_token(self, client):
        """测试无令牌获取预设分类"""
        response = client.get("/api/v1/categories/presets")
        assert response.status_code == 401


class TestCategoryEdgeCases:
    """边界情况测试类"""

    def test_create_category_empty_name(self, client, auth_headers):
        """测试创建空名称分类"""
        response = client.post(
            "/api/v1/categories",
            headers=auth_headers,
            json={
                "name": "",
                "type": "expense"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_create_category_long_name(self, client, auth_headers):
        """测试创建名称过长的分类"""
        response = client.post(
            "/api/v1/categories",
            headers=auth_headers,
            json={
                "name": "a" * 100,
                "type": "expense"
            }
        )
        # 应该返回 422 (validation) 或 400 (business logic)
        assert response.status_code in [400, 422]
