import os
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.models.user import User
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


from fastapi.testclient import TestClient
from app.auth.jwt import create_access_token


def get_auth_headers(test_user):
    """生成认证请求头"""
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


class TestProjectModel:
    """Project 模型测试类"""

    def test_create_project(self, db_session, test_user):
        """测试创建项目"""
        project = Project(
            name="旅行项目",
            description="2024年日本旅行",
            budget=10000.00,
            status="active",
            start_date=datetime.now(),
            owner_id=test_user.id,
            created_by_id=test_user.id
        )
        
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        
        assert project.id is not None
        assert project.name == "旅行项目"
        assert project.description == "2024年日本旅行"
        assert project.budget == 10000.00
        assert project.status == "active"
        assert project.owner_id == test_user.id

    def test_project_with_all_statuses(self, db_session, test_user):
        """测试项目所有状态"""
        statuses = ["active", "completed", "archived"]
        
        for status in statuses:
            project = Project(
                name=f"项目-{status}",
                status=status,
                owner_id=test_user.id,
            created_by_id=test_user.id
            )
            db_session.add(project)
            db_session.commit()
            db_session.refresh(project)
            
            assert project.status == status

    def test_project_nullable_fields(self, db_session, test_user):
        """测试可选字段"""
        project = Project(
            name="最小项目",
            # description, budget, start_date, end_date, updated_at 都是可选的
            owner_id=test_user.id,
            created_by_id=test_user.id
        )
        
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        
        assert project.description is None
        assert project.budget is None
        assert project.start_date is None
        assert project.end_date is None
        assert project.updated_at is None

    def test_project_owner_relationship(self, db_session, test_user):
        """测试项目与创建者的关系"""
        project = Project(
            name="个人项目",
            owner_id=test_user.id,
            created_by_id=test_user.id
        )
        
        db_session.add(project)
        db_session.commit()
        
        assert project.owner.username == "testuser"
        assert project.created_by.username == "testuser"

    def test_project_records_relationship(self, db_session, test_user):
        """测试项目与记账记录的关系"""
        # 创建项目
        project = Project(
            name="旅行项目",
            owner_id=test_user.id,
            created_by_id=test_user.id
        )
        db_session.add(project)
        db_session.commit()
        
        # 创建多条记录
        for i in range(3):
            record = Record(
                user_id=test_user.id,
                amount=100.00 * (i + 1),
                type=RecordType.EXPENSE,
                description=f"支出{i + 1}",
                date=datetime.now(),
                project_id=project.id
            )
            db_session.add(record)
        
        db_session.commit()
        
        # 验证关系
        assert len(project.records) == 3
        assert project.records[0].amount == 100.00
        assert project.records[1].amount == 200.00
        assert project.records[2].amount == 300.00

    def test_project_without_records(self, db_session, test_user):
        """测试没有记录的项目"""
        project = Project(
            name="空项目",
            owner_id=test_user.id,
            created_by_id=test_user.id
        )
        
        db_session.add(project)
        db_session.commit()
        
        assert len(project.records) == 0

    def test_project_total_expenses(self, db_session, test_user):
        """测试计算项目总支出"""
        project = Project(
            name="消费项目",
            owner_id=test_user.id,
            created_by_id=test_user.id
        )
        db_session.add(project)
        db_session.commit()
        
        # 创建记录
        records_data = [
            {"amount": 100.00, "description": "餐饮"},
            {"amount": 200.00, "description": "交通"},
            {"amount": 300.00, "description": "住宿"},
        ]
        
        for data in records_data:
            record = Record(
                user_id=test_user.id,
                amount=data["amount"],
                type=RecordType.EXPENSE,
                description=data["description"],
                date=datetime.now(),
                project_id=project.id
            )
            db_session.add(record)
        
        db_session.commit()
        
        total = sum(r.amount for r in project.records)
        assert total == 600.00

    def test_multiple_projects_per_user(self, db_session, test_user):
        """测试用户可以有多个项目"""
        projects = [
            Project(name="项目1", owner_id=test_user.id, created_by_id=test_user.id),
            Project(name="项目2", owner_id=test_user.id, created_by_id=test_user.id),
            Project(name="项目3", owner_id=test_user.id, created_by_id=test_user.id),
        ]
        
        for p in projects:
            db_session.add(p)
        
        db_session.commit()
        
        user_projects = test_user.projects
        assert len(user_projects) == 3
        assert user_projects[0].name == "项目1"
        assert user_projects[1].name == "项目2"
        assert user_projects[2].name == "项目3"


class TestProjectRouter:
    """Project Router 测试类"""

    def test_create_project(self, client, test_user):
        """测试创建项目"""
        project_data = {
            "name": "新项目",
            "description": "测试项目",
            "budget": 5000.00,
            "status": "active"
        }
        
        response = client.post(
            "/api/v1/projects",
            json=project_data,
            headers=get_auth_headers(test_user)
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "新项目"
        assert data["description"] == "测试项目"
        assert data["budget"] == 5000.00
        assert data["status"] == "active"

    def test_get_projects_list(self, client, test_user):
        """测试获取项目列表"""
        # 创建测试项目
        for i in range(3):
            client.post(
                "/api/v1/projects",
                json={"name": f"项目{i + 1}"},
                headers=get_auth_headers(test_user)
            )
        
        response = client.get(
            "/api/v1/projects",
            headers=get_auth_headers(test_user)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert "total" in data
        assert len(data["projects"]) >= 3

    def test_get_project_detail(self, client, test_user):
        """测试获取项目详情"""
        create_response = client.post(
            "/api/v1/projects",
            json={
                "name": "详情测试项目",
                "budget": 10000.00
            },
            headers=get_auth_headers(test_user)
        )
        project_id = create_response.json()["id"]
        
        response = client.get(
            f"/api/v1/projects/{project_id}",
            headers=get_auth_headers(test_user)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "详情测试项目"
        assert data["budget"] == 10000.00

    def test_update_project(self, client, test_user):
        """测试更新项目"""
        create_response = client.post(
            "/api/v1/projects",
            json={
                "name": "原名称",
                "budget": 1000.00
            },
            headers=get_auth_headers(test_user)
        )
        project_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/v1/projects/{project_id}",
            json={
                "name": "更新名称",
                "budget": 2000.00,
                "status": "completed"
            },
            headers=get_auth_headers(test_user)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新名称"
        assert data["budget"] == 2000.00
        assert data["status"] == "completed"

    def test_delete_project(self, client, test_user):
        """测试删除项目"""
        create_response = client.post(
            "/api/v1/projects",
            json={"name": "待删除项目"},
            headers=get_auth_headers(test_user)
        )
        project_id = create_response.json()["id"]
        
        response = client.delete(
            f"/api/v1/projects/{project_id}",
            headers=get_auth_headers(test_user)
        )
        
        assert response.status_code == 200
        
        # 验证已删除
        detail_response = client.get(
            f"/api/v1/projects/{project_id}",
            headers=get_auth_headers(test_user)
        )
        assert detail_response.status_code == 404

    def test_filter_projects_by_status(self, client, test_user):
        """测试按状态筛选项目"""
        # 创建不同状态的项目
        client.post(
            "/api/v1/projects",
            json={"name": "进行中项目", "status": "active"},
            headers=get_auth_headers(test_user)
        )
        client.post(
            "/api/v1/projects",
            json={"name": "已完成项目", "status": "completed"},
            headers=get_auth_headers(test_user)
        )
        
        # 只筛选进行中
        response = client.get(
            "/api/v1/projects?status=active",
            headers=get_auth_headers(test_user)
        )
        
        assert response.status_code == 200
        data = response.json()
        for project in data["projects"]:
            assert project["status"] == "active"

    def test_project_with_records(self, client, test_user, db_session):
        """测试项目关联记录"""
        # 先创建项目
        create_response = client.post(
            "/api/v1/projects",
            json={"name": "旅行项目"},
            headers=get_auth_headers(test_user)
        )
        project_id = create_response.json()["id"]
        
        # 先创建分类
        category_response = client.post(
            "/api/v1/categories",
            json={"name": "测试分类", "type": "expense", "icon": "test", "color": "#000000"},
            headers=get_auth_headers(test_user)
        )
        category_id = category_response.json()["id"]
        
        # 创建记录
        for i in range(2):
            client.post(
                "/api/v1/records",
                json={
                    "amount": 100.00 * (i + 1),
                    "type": "expense",
                    "description": f"支出{i + 1}",
                    "date": datetime.now().isoformat(),
                    "project_id": project_id,
                    "category_id": category_id
                },
                headers=get_auth_headers(test_user)
            )
        
        # 验证项目详情包含记录
        response = client.get(
            f"/api/v1/projects/{project_id}",
            headers=get_auth_headers(test_user)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "records" in data
        assert len(data["records"]) == 2

    def test_unauthorized_access(self, client):
        """测试未授权访问"""
        response = client.get("/api/v1/projects")
        assert response.status_code == 401
