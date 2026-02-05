import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app

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


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.mark.asyncio
async def test_user_model(test_db):
    """测试用户模型创建"""
    from app.models.user import User
    
    db = TestingSessionLocal()
    try:
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_verified is False
    finally:
        db.close()


@pytest.mark.asyncio
async def test_category_model(test_db):
    """测试分类模型创建"""
    from app.models.category import Category, CategoryType, CategoryLevel
    from app.models.user import User
    
    db = TestingSessionLocal()
    try:
        # 先创建用户
        user = User(
            username="categorytest",
            email="category@example.com",
            hashed_password="hashed"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 创建一级分类
        category = Category(
            name="餐饮",
            type=CategoryType.EXPENSE,
            level=CategoryLevel.PRIMARY,
            icon="food",
            color="#FF5722",
            user_id=user.id
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        
        assert category.id is not None
        assert category.name == "餐饮"
        assert category.type == CategoryType.EXPENSE
        assert category.level == CategoryLevel.PRIMARY
        assert category.user_id == user.id
    finally:
        db.close()


@pytest.mark.asyncio
async def test_record_model(test_db):
    """测试记账记录模型创建"""
    from app.models.record import Record, RecordType
    from app.models.user import User
    from app.models.category import Category, CategoryType
    
    db = TestingSessionLocal()
    try:
        # 创建用户和分类
        user = User(
            username="recordtest",
            email="record@example.com",
            hashed_password="hashed"
        )
        db.add(user)
        db.commit()
        
        category = Category(
            name="购物",
            type=CategoryType.EXPENSE,
            user_id=user.id
        )
        db.add(category)
        db.commit()
        
        # 创建记录
        from datetime import datetime
        import pytz
        
        shanghai_tz = pytz.timezone("Asia/Shanghai")
        record = Record(
            type=RecordType.EXPENSE,
            amount=10000,  # 100元
            description="午餐",
            note="在公司附近吃的",
            payer_count=1,
            total_people=1,
            payment_method=None,
            date=datetime.now(shanghai_tz),
            user_id=user.id,
            category_id=category.id
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        
        assert record.id is not None
        assert record.amount == 10000
        assert record.type == RecordType.EXPENSE
        assert record.user_id == user.id
    finally:
        db.close()


@pytest.mark.asyncio
async def test_project_model(test_db):
    """测试项目模型创建"""
    from app.models.project import Project
    from app.models.user import User
    
    db = TestingSessionLocal()
    try:
        user = User(
            username="projecttest",
            email="project@example.com",
            hashed_password="hashed"
        )
        db.add(user)
        db.commit()
        
        project = Project(
            name="云南旅行",
            description="2024年云南之旅",
            color="#3498DB",
            owner_id=user.id
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        assert project.id is not None
        assert project.name == "云南旅行"
        assert project.owner_id == user.id
        assert project.is_active is True
    finally:
        db.close()


@pytest.mark.asyncio
async def test_budget_model(test_db):
    """测试预算模型创建"""
    from app.models.budget import Budget, BudgetPeriod
    from app.models.user import User
    
    db = TestingSessionLocal()
    try:
        user = User(
            username="budgettest",
            email="budget@example.com",
            hashed_password="hashed"
        )
        db.add(user)
        db.commit()
        
        budget = Budget(
            name="月度餐饮预算",
            amount=500000,  # 5000元
            period=BudgetPeriod.MONTHLY,
            alert_threshold=80,
            user_id=user.id
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
        
        assert budget.id is not None
        assert budget.name == "月度餐饮预算"
        assert budget.amount == 500000
        assert budget.period == BudgetPeriod.MONTHLY
    finally:
        db.close()


@pytest.mark.asyncio
async def test_invitation_code_model(test_db):
    """测试邀请码模型创建"""
    from app.models.invitation import InvitationCode
    from app.models.user import User
    
    db = TestingSessionLocal()
    try:
        user = User(
            username="invite_test",
            email="invite@example.com",
            hashed_password="hashed"
        )
        db.add(user)
        db.commit()
        
        code = InvitationCode(
            code=InvitationCode.generate_code(),
            max_uses=3,
            created_by_id=user.id
        )
        db.add(code)
        db.commit()
        db.refresh(code)
        
        assert code.id is not None
        assert code.code is not None
        assert len(code.code) == 10
        assert code.max_uses == 3
        assert code.current_uses == 0
        assert code.can_use is True
    finally:
        db.close()
