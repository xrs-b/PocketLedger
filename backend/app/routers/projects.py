from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List

from app.database import get_db
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.models.record import Record, RecordType
from app.auth.jwt import get_current_user
from app.schemas.project import (
    ProjectResponse,
    ProjectCreate,
    ProjectUpdate,
    ProjectListResponse,
    ProjectStats
)

router = APIRouter(prefix="/projects", tags=["项目管理"])


@router.get("", response_model=ProjectListResponse)
async def get_projects(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目列表（支持状态筛选和分页）"""
    query = db.query(Project).filter(Project.owner_id == current_user.id)
    
    # 状态筛选
    if status:
        query = query.filter(Project.status == status)
    
    # 获取总数
    total = query.count()
    
    # 分页
    projects = query.order_by(Project.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "projects": projects,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建项目"""
    project = Project(
        name=project_data.name,
        description=project_data.description,
        budget=project_data.budget,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        owner_id=current_user.id,
        created_by_id=current_user.id,
        status=ProjectStatus.ACTIVE
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目详情"""
    project = db.query(Project).options(
        joinedload(Project.records)
    ).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 转换为字典并添加 records 字段
    result = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "budget": project.budget,
        "status": project.status,
        "start_date": project.start_date,
        "end_date": project.end_date,
        "created_by_id": project.created_by_id,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "records": [
            {k: v for k, v in record.__dict__.items() if not k.startswith('_sa_')}
            for record in project.records
        ]
    }
    
    return result


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新项目"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 更新字段
    if project_data.name is not None:
        project.name = project_data.name
    
    if project_data.description is not None:
        project.description = project_data.description
    
    if project_data.budget is not None:
        project.budget = project_data.budget
    
    if project_data.status is not None:
        project.status = project_data.status
    
    if project_data.start_date is not None:
        project.start_date = project_data.start_date
    
    if project_data.end_date is not None:
        project.end_date = project_data.end_date
    
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/{project_id}", response_model=dict)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除项目"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    db.delete(project)
    db.commit()
    
    return {"message": "项目删除成功"}


@router.get("/{project_id}/stats", response_model=ProjectStats)
async def get_project_stats(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目统计"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 访问 records 以触发加载
    records = project.records
    
    # 计算统计数据
    total_budget = project.budget or 0.0
    total_expenses = sum(
        record.amount for record in records 
        if record.type == RecordType.EXPENSE
    )
    total_income = sum(
        record.amount for record in records 
        if record.type == RecordType.INCOME
    )
    balance = total_income - total_expenses
    
    return {
        "total_budget": total_budget,
        "total_expenses": total_expenses,
        "total_income": total_income,
        "balance": balance
    }
