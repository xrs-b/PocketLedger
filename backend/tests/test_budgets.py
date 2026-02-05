import pytest
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.category import Category, CategoryType
from app.models.budget import Budget, BudgetPeriodType
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


from fastapi.testclient import TestClient
from app.auth.jwt import create_access_token


def get_auth_headers(test_user):
    """生成认证请求头"""
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


class TestBudgetModel:
    """Budget 模型测试类"""

    def test_create_budget(self, db_session, test_user):
        """测试创建预算"""
        budget = Budget(
            name="月度餐饮预算",
            amount=2000.00,
            period_type=BudgetPeriodType.MONTHLY,
            start_date=datetime.now(),
            user_id=test_user.id,
            is_active=True
        )
        
        db_session.add(budget)
        db_session.commit()
        db_session.refresh(budget)
        
        assert budget.id is not None
        assert budget.name == "月度餐饮预算"
        assert budget.amount == 2000.00
        assert budget.period_type == BudgetPeriodType.MONTHLY
        assert budget.user_id == test_user.id
        assert budget.is_active is True

    def test_budget_with_category(self, db_session, test_user):
        """测试带分类的预算"""
        # 创建分类
        category = Category(
            name="餐饮",
            type=CategoryType.EXPENSE,
            user_id=test_user.id
        )
        db_session.add(category)
        db_session.commit()
        
        budget = Budget(
            name="餐饮预算",
            amount=1500.00,
            period_type=BudgetPeriodType.MONTHLY,
            start_date=datetime.now(),
            user_id=test_user.id,
            category_id=category.id
        )
        
        db_session.add(budget)
        db_session.commit()
        db_session.refresh(budget)
        
        assert budget.category_id == category.id
        assert budget.category.name == "餐饮"

    def test_budget_with_yearly_period(self, db_session, test_user):
        """测试年度预算"""
        budget = Budget(
            name="年度旅行预算",
            amount=30000.00,
            period_type=BudgetPeriodType.YEARLY,
            start_date=datetime.now(),
            end_date=datetime(2025, 12, 31),
            user_id=test_user.id
        )
        
        db_session.add(budget)
        db_session.commit()
        db_session.refresh(budget)
        
        assert budget.period_type == BudgetPeriodType.YEARLY
        assert budget.end_date is not None

    def test_budget_nullable_fields(self, db_session, test_user):
        """测试可选字段"""
        budget = Budget(
            name="最小预算",
            amount=100.00,
            period_type=BudgetPeriodType.MONTHLY,
            start_date=datetime.now(),
            user_id=test_user.id
            # category_id, end_date 都是可选的
        )
        
        db_session.add(budget)
        db_session.commit()
        db_session.refresh(budget)
        
        assert budget.category_id is None
        assert budget.end_date is None
        # updated_at 在创建时会设置默认值
        assert budget.updated_at is not None
        assert budget.is_active is True  # 默认值

    def test_budget_user_relationship(self, db_session, test_user):
        """测试预算与用户的关系"""
        budget = Budget(
            name="个人预算",
            amount=5000.00,
            period_type=BudgetPeriodType.MONTHLY,
            start_date=datetime.now(),
            user_id=test_user.id
        )
        
        db_session.add(budget)
        db_session.commit()
        
        assert budget.user.username == "testuser"

    def test_budget_inactive(self, db_session, test_user):
        """测试非激活状态预算"""
        budget = Budget(
            name="已禁用预算",
            amount=1000.00,
            period_type=BudgetPeriodType.MONTHLY,
            start_date=datetime.now(),
            user_id=test_user.id,
            is_active=False
        )
        
        db_session.add(budget)
        db_session.commit()
        db_session.refresh(budget)
        
        assert budget.is_active is False

    def test_multiple_budgets_per_user(self, db_session, test_user):
        """测试用户可以有多个预算"""
        budgets = [
            Budget(name="餐饮预算", amount=2000.00, period_type=BudgetPeriodType.MONTHLY, start_date=datetime.now(), user_id=test_user.id),
            Budget(name="娱乐预算", amount=1000.00, period_type=BudgetPeriodType.MONTHLY, start_date=datetime.now(), user_id=test_user.id),
            Budget(name="旅行预算", amount=15000.00, period_type=BudgetPeriodType.YEARLY, start_date=datetime.now(), user_id=test_user.id),
        ]
        
        for b in budgets:
            db_session.add(b)
        
        db_session.commit()
        
        # 验证创建了3个预算
        all_budgets = db_session.query(Budget).filter(Budget.user_id == test_user.id).all()
        assert len(all_budgets) == 3

    def test_budget_period_types(self, db_session, test_user):
        """测试预算周期类型"""
        monthly = Budget(name="月预算", amount=1000.00, period_type=BudgetPeriodType.MONTHLY, start_date=datetime.now(), user_id=test_user.id)
        yearly = Budget(name="年预算", amount=12000.00, period_type=BudgetPeriodType.YEARLY, start_date=datetime.now(), user_id=test_user.id)
        
        db_session.add_all([monthly, yearly])
        db_session.commit()
        
        assert monthly.period_type == "monthly"
        assert yearly.period_type == "yearly"

    def test_budget_without_category(self, db_session, test_user):
        """测试不带分类的预算"""
        budget = Budget(
            name="总预算",
            amount=5000.00,
            period_type=BudgetPeriodType.MONTHLY,
            start_date=datetime.now(),
            user_id=test_user.id,
            category_id=None  # 显式设置为 None
        )
        
        db_session.add(budget)
        db_session.commit()
        db_session.refresh(budget)
        
        assert budget.category_id is None

    def test_budget_default_values(self, db_session, test_user):
        """测试预算默认值"""
        budget = Budget(
            name="默认测试预算",
            amount=100.00,
            period_type=BudgetPeriodType.MONTHLY,
            start_date=datetime.now(),
            user_id=test_user.id
        )
        
        db_session.add(budget)
        db_session.commit()
        db_session.refresh(budget)
        
        # is_active 默认为 True
        assert budget.is_active is True
        # created_at 应该自动设置
        assert budget.created_at is not None
