import os
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.category import Category, CategoryType
from app.models.record import Record, RecordType
from app.models.project import Project
from app.auth.password import get_password_hash
from fastapi.testclient import TestClient
from app.auth.jwt import create_access_token

# 设置测试环境变量
os.environ["TESTING"] = "1"

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
def test_category(db_session, test_user):
    """创建测试分类"""
    category = Category(
        name="餐饮",
        type=CategoryType.EXPENSE,
        user_id=test_user.id
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_income_category(db_session, test_user):
    """创建测试收入分类"""
    category = Category(
        name="工资",
        type=CategoryType.INCOME,
        user_id=test_user.id
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_project(db_session, test_user):
    """创建测试项目"""
    project = Project(
        name="旅行项目",
        owner_id=test_user.id,
        created_by_id=test_user.id
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def test_records(db_session, test_user, test_category, test_income_category, test_project):
    """创建测试记录"""
    now = datetime.now()
    
    records = [
        # 收入记录
        Record(
            user_id=test_user.id,
            category_id=test_income_category.id,
            amount=5000.00,
            type=RecordType.INCOME,
            description="工资",
            date=now
        ),
        # 支出记录
        Record(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=500.00,
            type=RecordType.EXPENSE,
            description="午餐",
            date=now
        ),
        Record(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=300.00,
            type=RecordType.EXPENSE,
            description="晚餐",
            date=now
        ),
    ]
    
    for r in records:
        db_session.add(r)
    db_session.commit()
    return records


def get_auth_headers(test_user):
    """生成认证请求头"""
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


class TestStatisticsAPI:
    """Statistics API 测试类"""

    def test_monthly_statistics(self, client, test_user, test_records, db_session):
        """测试月度统计"""
        now = datetime.now()
        response = client.get(
            f"/api/v1/statistics/monthly?year={now.year}&month={now.month}",
            headers=get_auth_headers(test_user)
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "total_expense" in data
        assert "balance" in data

    def test_range_statistics(self, client, test_user, test_records):
        """测试时间段统计"""
        now = datetime.now()
        date_from = now.replace(day=1).strftime("%Y-%m-%d")
        date_to = now.strftime("%Y-%m-%d")
        
        response = client.get(
            f"/api/v1/statistics/range?date_from={date_from}&date_to={date_to}",
            headers=get_auth_headers(test_user)
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "total_expense" in data
        assert "balance" in data

    def test_category_statistics_expense(self, client, test_user, test_records):
        """测试分类支出统计"""
        now = datetime.now()
        date_from = now.replace(day=1).strftime("%Y-%m-%d")
        date_to = now.strftime("%Y-%m-%d")
        
        response = client.get(
            f"/api/v1/statistics/categories?date_from={date_from}&date_to={date_to}&type=expense",
            headers=get_auth_headers(test_user)
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_category_statistics_income(self, client, test_user, test_records):
        """测试分类收入统计"""
        now = datetime.now()
        date_from = now.replace(day=1).strftime("%Y-%m-%d")
        date_to = now.strftime("%Y-%m-%d")
        
        response = client.get(
            f"/api/v1/statistics/categories?date_from={date_from}&date_to={date_to}&type=income",
            headers=get_auth_headers(test_user)
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_project_statistics(self, client, test_user, test_records, db_session, test_project):
        """测试项目统计"""
        # 为项目添加一些记录
        now = datetime.now()
        expense_record = Record(
            user_id=test_user.id,
            project_id=test_project.id,
            amount=1000.00,
            type=RecordType.EXPENSE,
            description="项目支出",
            date=now
        )
        income_record = Record(
            user_id=test_user.id,
            project_id=test_project.id,
            amount=2000.00,
            type=RecordType.INCOME,
            description="项目收入",
            date=now
        )
        db_session.add(expense_record)
        db_session.add(income_record)
        db_session.commit()
        
        response = client.get(
            "/api/v1/statistics/projects",
            headers=get_auth_headers(test_user)
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_overview_statistics(self, client, test_user, test_records):
        """测试综合概览"""
        now = datetime.now()
        date_from = now.replace(day=1).strftime("%Y-%m-%d")
        date_to = now.strftime("%Y-%m-%d")
        
        response = client.get(
            f"/api/v1/statistics/overview?date_from={date_from}&date_to={date_to}",
            headers=get_auth_headers(test_user)
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_income" in data
        assert "total_expense" in data
        assert "balance" in data
        assert "top_categories" in data
        assert "top_projects" in data

    def test_unauthorized_access(self, client):
        """测试未授权访问"""
        response = client.get("/api/v1/statistics/monthly?year=2024&month=1")
        assert response.status_code == 401
