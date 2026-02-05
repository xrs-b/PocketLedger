import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.config import settings

# 测试引擎（SQLite 内存）
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# 生产引擎（MySQL）
if os.environ.get("TESTING") != "1":
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600
    )
else:
    # 测试时使用测试引擎
    engine = test_engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_test_db():
    """初始化测试数据库"""
    Base.metadata.create_all(bind=test_engine)


def cleanup_test_db():
    """清理测试数据库"""
    Base.metadata.drop_all(bind=test_engine)
