from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.record import Record, RecordType
from app.models.category import Category
from app.models.project import Project
from app.auth.jwt import get_current_user
from app.schemas.record import (
    RecordResponse,
    RecordCreate,
    RecordUpdate,
    RecordListResponse,
    RecordWithCategory
)

router = APIRouter(prefix="/records", tags=["记账记录"])


@router.get("", response_model=RecordListResponse)
async def get_records(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    category_id: Optional[int] = None,
    type: Optional[RecordType] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取记账记录列表（支持筛选和分页）"""
    query = db.query(Record).filter(Record.user_id == current_user.id)
    
    # 日期范围筛选
    if date_from:
        query = query.filter(Record.date >= date_from)
    if date_to:
        query = query.filter(Record.date <= date_to)
    
    # 分类筛选
    if category_id:
        # 验证分类存在
        category = db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == current_user.id,
            Category.is_active == True
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
        query = query.filter(Record.category_id == category_id)
    
    # 类型筛选
    if type:
        query = query.filter(Record.type == type)
    
    # 获取总数
    total = query.count()
    
    # 分页
    records = query.order_by(Record.date.desc(), Record.id.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "records": records,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
async def create_record(
    record_data: RecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建记账记录"""
    # 验证分类存在
    category = db.query(Category).filter(
        Category.id == record_data.category_id,
        Category.is_active == True
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分类不存在"
        )
    
    # 如果指定了项目，验证项目存在且属于当前用户
    if record_data.project_id:
        project = db.query(Project).filter(
            Project.id == record_data.project_id,
            Project.owner_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
    
    # 创建记录
    record = Record(
        user_id=current_user.id,
        category_id=record_data.category_id,
        amount=record_data.amount,
        type=record_data.type,
        description=record_data.description,
        date=record_data.date,
        payer_count=record_data.payer_count or 1,
        is_aa=record_data.is_aa or False,
        project_id=record_data.project_id
    )
    
    # 计算人均分摊
    record.payer_per_share = record.calculate_per_share()
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return record


@router.get("/{record_id}", response_model=RecordWithCategory)
async def get_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取记账记录详情"""
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    return record


@router.put("/{record_id}", response_model=RecordResponse)
async def update_record(
    record_id: int,
    record_data: RecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新记账记录"""
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    # 更新字段
    if record_data.category_id is not None:
        # 验证分类存在
        category = db.query(Category).filter(
            Category.id == record_data.category_id,
            Category.is_active == True
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
        record.category_id = record_data.category_id
    
    if record_data.amount is not None:
        record.amount = record_data.amount
    
    if record_data.description is not None:
        record.description = record_data.description
    
    if record_data.date is not None:
        record.date = record_data.date
    
    if record_data.payer_count is not None:
        record.payer_count = record_data.payer_count
    
    if record_data.is_aa is not None:
        record.is_aa = record_data.is_aa
    
    if record_data.project_id is not None:
        if record_data.project_id:
            # 验证项目存在且属于当前用户
            project = db.query(Project).filter(
                Project.id == record_data.project_id,
                Project.owner_id == current_user.id
            ).first()
            
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="项目不存在"
                )
        record.project_id = record_data.project_id
    
    # 重新计算人均分摊
    record.payer_per_share = record.calculate_per_share()
    
    db.commit()
    db.refresh(record)
    
    return record


@router.delete("/{record_id}", response_model=dict)
async def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除记账记录"""
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    db.delete(record)
    db.commit()
    
    return {"message": "记录删除成功"}


@router.post("/{record_id}/project", response_model=RecordResponse)
async def link_record_to_project(
    record_id: int,
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """将记账记录关联到项目"""
    # 验证记录存在
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    # 验证项目存在且属于当前用户
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 关联项目
    record.project_id = project_id
    db.commit()
    db.refresh(record)
    
    return record


@router.delete("/{record_id}/project/{project_id}", response_model=RecordResponse)
async def unlink_record_from_project(
    record_id: int,
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消记账记录与项目的关联"""
    # 验证记录存在
    record = db.query(Record).filter(
        Record.id == record_id,
        Record.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    # 验证记录是否关联到指定项目
    if record.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="记录未关联到指定项目"
        )
    
    # 取消关联
    record.project_id = None
    db.commit()
    db.refresh(record)
    
    return record
