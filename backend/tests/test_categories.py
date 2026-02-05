import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.category import Category, CategoryType
from datetime import datetime
import pytz

shanghai_tz = pytz.timezone("Asia/Shanghai")


# 创建内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_database():
    """创建所有表"""
    Base.metadata.create_all(bind=engine)


def teardown_database():
    """清理所有表"""
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """提供数据库会话"""
    setup_database()
    session = TestingSessionLocal()
    yield session
    session.close()
    teardown_database()


@pytest.fixture
def sample_category(db_session):
    """提供示例分类"""
    category = Category(
        name="餐饮",
        type=CategoryType.EXPENSE,
        is_system=True,
        icon="food",
        sort_order=1,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def nested_categories(db_session):
    """提供嵌套分类（一级和二级）"""
    # 一级分类
    parent = Category(
        name="支出",
        type=CategoryType.EXPENSE,
        is_system=True,
        sort_order=0,
    )
    db_session.add(parent)
    db_session.commit()
    
    # 二级分类
    child = Category(
        name="餐饮",
        type=CategoryType.EXPENSE,
        parent_id=parent.id,
        is_system=True,
        icon="food",
        sort_order=1,
    )
    db_session.add(child)
    db_session.commit()
    db_session.refresh(child)
    
    return parent, child


class TestCategoryModel:
    """Category 模型测试类"""
    
    def test_create_category(self, db_session):
        """测试创建基本分类"""
        category = Category(
            name="工资",
            type=CategoryType.INCOME,
            is_system=True,
        )
        db_session.add(category)
        db_session.commit()
        
        assert category.id is not None
        assert category.name == "工资"
        assert category.type == CategoryType.INCOME
        assert category.is_system is True
        assert category.parent_id is None
        assert category.sort_order == 0
        assert category.created_at is not None
        assert category.icon is None
    
    def test_category_with_icon(self, db_session):
        """测试带图标的分类"""
        category = Category(
            name="交通",
            type=CategoryType.EXPENSE,
            icon="transport",
        )
        db_session.add(category)
        db_session.commit()
        
        assert category.icon == "transport"
    
    def test_category_with_parent(self, nested_categories):
        """测试带父分类的二级分类"""
        parent, child = nested_categories
        
        assert parent.id is not None
        assert child.parent_id == parent.id
        assert child.id != parent.id
    
    def test_parent_child_relationship(self, nested_categories):
        """测试父子关系"""
        parent, child = nested_categories
        
        # 检查反向关系（使用 children）
        assert len(parent.children) >= 1
        assert child in parent.children
    
    def test_category_type_enum(self, db_session):
        """测试分类类型"""
        income_category = Category(name="工资", type=CategoryType.INCOME)
        expense_category = Category(name="餐饮", type=CategoryType.EXPENSE)
        
        db_session.add_all([income_category, expense_category])
        db_session.commit()
        
        assert income_category.type == CategoryType.INCOME
        assert expense_category.type == CategoryType.EXPENSE
    
    def test_sort_order_default(self, db_session):
        """测试排序默认值"""
        category = Category(name="测试分类", type=CategoryType.EXPENSE)
        db_session.add(category)
        db_session.commit()
        
        assert category.sort_order == 0
    
    def test_system_default_false(self, db_session):
        """测试系统预设默认值"""
        category = Category(name="自定义分类", type=CategoryType.INCOME)
        db_session.add(category)
        db_session.commit()
        
        assert category.is_system is False
    
    def test_category_repr(self, sample_category):
        """测试 __repr__ 方法"""
        repr_str = repr(sample_category)
        assert "Category" in repr_str
        assert "餐饮" in repr_str
    
    def test_multiple_categories(self, db_session):
        """测试多个分类"""
        categories = [
            Category(name="工资", type=CategoryType.INCOME, is_system=True),
            Category(name="奖金", type=CategoryType.INCOME, is_system=True),
            Category(name="餐饮", type=CategoryType.EXPENSE, is_system=True),
            Category(name="交通", type=CategoryType.EXPENSE, is_system=True),
        ]
        
        for cat in categories:
            db_session.add(cat)
        db_session.commit()
        
        # 验证所有分类都已创建
        all_categories = db_session.query(Category).all()
        assert len(all_categories) == 4
    
    def test_category_type_value(self, db_session):
        """测试分类类型的实际值"""
        category = Category(
            name="测试",
            type=CategoryType.EXPENSE,
        )
        db_session.add(category)
        db_session.commit()
        
        # 验证存储的值
        assert category.type.value == "expense"
    
    def test_created_at_is_datetime(self, db_session):
        """测试 created_at 是 datetime 类型"""
        category = Category(name="测试", type=CategoryType.EXPENSE)
        db_session.add(category)
        db_session.commit()
        
        assert isinstance(category.created_at, datetime)
    
    def test_self_referential_parent(self, nested_categories):
        """测试自引用父分类"""
        parent, child = nested_categories
        
        # 确保父分类的 parent_id 是 None
        assert parent.parent_id is None
        # 确保子分类的 parent_id 指向父分类
        assert child.parent_id == parent.id
