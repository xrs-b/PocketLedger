import os
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.category import Category, CategoryType, CategoryLevel
from app.models.project import Project
from app.models.record import Record, RecordType
from app.auth.password import get_password_hash

# 设置测试环境变量
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
def sample_categories(db_session, test_user):
    """创建示例分类"""
    category = Category(
        name="餐饮",
        type=CategoryType.EXPENSE,
        level=CategoryLevel.PRIMARY,
        is_system=True,
        icon="food",
        user_id=test_user.id
    )
    
    income_category = Category(
        name="工资",
        type=CategoryType.INCOME,
        level=CategoryLevel.PRIMARY,
        is_system=True,
        icon="salary",
        user_id=test_user.id
    )
    
    db_session.add_all([category, income_category])
    db_session.commit()
    db_session.refresh(category)
    db_session.refresh(income_category)
    
    return category, income_category


from fastapi.testclient import TestClient
from app.auth.jwt import create_access_token


def get_auth_headers(test_user):
    """生成认证请求头"""
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


class TestRecordModel:
    """Record 模型测试类"""

    def test_create_record(self, db_session, test_user, sample_categories):
        """测试创建记账记录"""
        category = sample_categories[0]  # 使用支出分类
        
        record = Record(
            user_id=test_user.id,
            category_id=category.id,
            amount=100.50,
            type=RecordType.EXPENSE,
            description="测试支出",
            date=datetime.now()
        )
        
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)
        
        assert record.id is not None
        assert record.user_id == test_user.id
        assert record.category_id == category.id
        assert record.amount == 100.50
        assert record.type == RecordType.EXPENSE
        assert record.description == "测试支出"
        assert record.payer_count == 1  # 默认值
        assert record.is_aa is False  # 默认值

    def test_record_with_aa(self, db_session, test_user, sample_categories):
        """测试创建 AA 制记账记录"""
        category = sample_categories[0]
        
        record = Record(
            user_id=test_user.id,
            category_id=category.id,
            amount=300.00,
            type=RecordType.EXPENSE,
            description="聚餐 AA",
            date=datetime.now(),
            payer_count=3,
            is_aa=True
        )
        
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)
        
        assert record.payer_count == 3
        assert record.is_aa is True

    def test_calculate_per_share(self, db_session, test_user, sample_categories):
        """测试计算人均分摊金额"""
        category = sample_categories[0]
        
        # 非 AA 记录
        record1 = Record(
            user_id=test_user.id,
            category_id=category.id,
            amount=100.00,
            type=RecordType.EXPENSE,
            date=datetime.now(),
            payer_count=1,
            is_aa=False
        )
        assert record1.calculate_per_share() == 100.00
        
        # AA 记录，3 人分摊
        record2 = Record(
            user_id=test_user.id,
            category_id=category.id,
            amount=300.00,
            type=RecordType.EXPENSE,
            date=datetime.now(),
            payer_count=3,
            is_aa=True
        )
        assert record2.calculate_per_share() == 100.00

    def test_is_income(self, db_session, test_user, sample_categories):
        """测试判断是否为收入"""
        category_expense = sample_categories[0]  # 支出分类
        category_income = sample_categories[1]  # 收入分类
        
        expense_record = Record(
            user_id=test_user.id,
            category_id=category_expense.id,
            amount=100.00,
            type=RecordType.EXPENSE,
            date=datetime.now()
        )
        
        income_record = Record(
            user_id=test_user.id,
            category_id=category_income.id,
            amount=5000.00,
            type=RecordType.INCOME,
            date=datetime.now()
        )
        
        assert expense_record.is_income() is False
        assert income_record.is_income() is True

    def test_record_with_project(self, db_session, test_user, sample_categories):
        """测试记账记录关联项目"""
        category = sample_categories[0]
        
        # 创建项目
        project = Project(
            name="旅行项目",
            owner_id=test_user.id
        )
        db_session.add(project)
        db_session.commit()
        
        record = Record(
            user_id=test_user.id,
            category_id=category.id,
            amount=500.00,
            type=RecordType.EXPENSE,
            description="旅行支出",
            date=datetime.now(),
            project_id=project.id
        )
        
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)
        
        assert record.project_id == project.id
        assert record.project.name == "旅行项目"

    def test_record_nullable_fields(self, db_session, test_user, sample_categories):
        """测试可选字段"""
        category = sample_categories[0]
        
        record = Record(
            user_id=test_user.id,
            category_id=category.id,
            amount=50.00,
            type=RecordType.EXPENSE,
            date=datetime.now()
            # description, project_id, payer_per_share 都是可选的
        )
        
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)
        
        assert record.description is None
        assert record.project_id is None
        assert record.payer_per_share is None

    def test_record_relationships(self, db_session, test_user, sample_categories):
        """测试记录的关系"""
        category = sample_categories[0]
        
        record = Record(
            user_id=test_user.id,
            category_id=category.id,
            amount=200.00,
            type=RecordType.EXPENSE,
            description="关系测试",
            date=datetime.now()
        )
        
        db_session.add(record)
        db_session.commit()
        
        # 验证关系
        assert record.user.username == "testuser"
        assert record.category.name == "餐饮"


class TestRecordRouter:
    """Record Router 测试类"""

    def test_create_record(self, client, test_user, sample_categories):
        """测试创建记账记录"""
        category = sample_categories[0]
        record_data = {
            "category_id": category.id,
            "amount": 150.00,
            "type": "expense",
            "description": "午餐",
            "date": datetime.now().isoformat()
        }
        
        response = client.post(
            "/api/v1/records",
            json=record_data,
            headers=get_auth_headers(test_user)
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 150.00
        assert data["description"] == "午餐"
        assert data["category_id"] == category.id

    def test_get_records_list(self, client, test_user, sample_categories):
        """测试获取记录列表"""
        category = sample_categories[0]
        
        # 创建测试记录
        record1 = Record(
            user_id=test_user.id,
            category_id=category.id,
            amount=100.00,
            type=RecordType.EXPENSE,
            description="测试1",
            date=datetime.now()
        )
        record2 = Record(
            user_id=test_user.id,
            category_id=category.id,
            amount=200.00,
            type=RecordType.EXPENSE,
            description="测试2",
            date=datetime.now()
        )
        
        client.post(
            "/api/v1/records",
            json={
                "category_id": category.id,
                "amount": 100.00,
                "type": "expense",
                "description": "测试1",
                "date": datetime.now().isoformat()
            },
            headers=get_auth_headers(test_user)
        )
        client.post(
            "/api/v1/records",
            json={
                "category_id": category.id,
                "amount": 200.00,
                "type": "expense",
                "description": "测试2",
                "date": datetime.now().isoformat()
            },
            headers=get_auth_headers(test_user)
        )
        
        response = client.get(
            "/api/v1/records",
            headers=get_auth_headers(test_user)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "records" in data
        assert "total" in data
        assert len(data["records"]) >= 2

    def test_get_record_detail(self, client, test_user, sample_categories):
        """测试获取记录详情"""
        category = sample_categories[0]
        
        # 先创建记录
        create_response = client.post(
            "/api/v1/records",
            json={
                "category_id": category.id,
                "amount": 300.00,
                "type": "expense",
                "description": "详情测试",
                "date": datetime.now().isoformat()
            },
            headers=get_auth_headers(test_user)
        )
        record_id = create_response.json()["id"]
        
        response = client.get(
            f"/api/v1/records/{record_id}",
            headers=get_auth_headers(test_user)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 300.00
        assert data["description"] == "详情测试"

    def test_update_record(self, client, test_user, sample_categories):
        """测试更新记录"""
        category = sample_categories[0]
        
        # 创建记录
        create_response = client.post(
            "/api/v1/records",
            json={
                "category_id": category.id,
                "amount": 100.00,
                "type": "expense",
                "description": "原描述",
                "date": datetime.now().isoformat()
            },
            headers=get_auth_headers(test_user)
        )
        record_id = create_response.json()["id"]
        
        # 更新记录
        response = client.put(
            f"/api/v1/records/{record_id}",
            json={
                "amount": 150.00,
                "description": "更新后的描述"
            },
            headers=get_auth_headers(test_user)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 150.00
        assert data["description"] == "更新后的描述"

    def test_delete_record(self, client, test_user, sample_categories):
        """测试删除记录"""
        category = sample_categories[0]
        
        # 创建记录
        create_response = client.post(
            "/api/v1/records",
            json={
                "category_id": category.id,
                "amount": 50.00,
                "type": "expense",
                "description": "待删除",
                "date": datetime.now().isoformat()
            },
            headers=get_auth_headers(test_user)
        )
        record_id = create_response.json()["id"]
        
        # 删除记录
        response = client.delete(
            f"/api/v1/records/{record_id}",
            headers=get_auth_headers(test_user)
        )
        
        assert response.status_code == 200
        
        # 验证已删除
        detail_response = client.get(
            f"/api/v1/records/{record_id}",
            headers=get_auth_headers(test_user)
        )
        assert detail_response.status_code == 404

    def test_filter_records_by_type(self, client, test_user, sample_categories):
        """测试按类型筛选记录"""
        expense_category = sample_categories[0]
        income_category = sample_categories[1]
        
        # 创建支出记录
        client.post(
            "/api/v1/records",
            json={
                "category_id": expense_category.id,
                "amount": 100.00,
                "type": "expense",
                "description": "支出",
                "date": datetime.now().isoformat()
            },
            headers=get_auth_headers(test_user)
        )
        
        # 创建收入记录
        client.post(
            "/api/v1/records",
            json={
                "category_id": income_category.id,
                "amount": 5000.00,
                "type": "income",
                "description": "工资",
                "date": datetime.now().isoformat()
            },
            headers=get_auth_headers(test_user)
        )
        
        # 只筛选支出
        response = client.get(
            "/api/v1/records?type=expense",
            headers=get_auth_headers(test_user)
        )
        
        assert response.status_code == 200
        data = response.json()
        for record in data["records"]:
            assert record["type"] == "expense"

    def test_records_with_project(self, client, test_user, sample_categories, db_session):
        """测试记录关联项目"""
        category = sample_categories[0]
        
        # 直接在数据库中创建项目
        project = Project(
            name="旅行",
            owner_id=test_user.id
        )
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        project_id = project.id
        
        # 创建关联项目的记录
        create_response = client.post(
            "/api/v1/records",
            json={
                "category_id": category.id,
                "amount": 500.00,
                "type": "expense",
                "description": "旅行支出",
                "date": datetime.now().isoformat(),
                "project_id": project_id
            },
            headers=get_auth_headers(test_user)
        )
        
        assert create_response.status_code == 201
        record_id = create_response.json()["id"]
        
        # 验证关联
        response = client.get(
            f"/api/v1/records/{record_id}",
            headers=get_auth_headers(test_user)
        )
        assert response.json()["project_id"] == project_id

    def test_unauthorized_access(self, client):
        """测试未授权访问"""
        response = client.get("/api/v1/records")
        assert response.status_code == 401
