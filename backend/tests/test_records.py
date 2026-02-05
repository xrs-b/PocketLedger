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
