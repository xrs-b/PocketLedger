from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.budget import Budget, BudgetPeriodType
from app.models.record import Record, RecordType
from app.models.category import Category
from app.auth.jwt import get_current_user
from app.schemas.budget import (
    BudgetResponse,
    BudgetCreate,
    BudgetUpdate,
    BudgetListResponse,
    BudgetAlert
)

router = APIRouter(prefix="/budgets", tags=["预算管理"])


class AlertsResponse(BaseModel):
    alerts: list[BudgetAlert]


@router.get("", response_model=BudgetListResponse)
async def get_budgets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取预算列表（支持分页）"""
    query = db.query(Budget).filter(Budget.user_id == current_user.id)
    
    # 获取总数
    total = query.count()
    
    # 分页
    budgets = query.order_by(Budget.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return {
        "budgets": budgets,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建预算"""
    # 验证分类存在（如果提供了category_id）
    if budget_data.category_id:
        category = db.query(Category).filter(
            Category.id == budget_data.category_id,
            Category.user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分类不存在"
            )
    
    budget = Budget(
        name=budget_data.name,
        amount=budget_data.amount,
        period_type=BudgetPeriodType(budget_data.period_type),
        start_date=budget_data.start_date,
        end_date=budget_data.end_date,
        category_id=budget_data.category_id,
        user_id=current_user.id
    )
    
    db.add(budget)
    db.commit()
    db.refresh(budget)
    
    return budget


@router.get("/alerts", response_model=AlertsResponse)
async def get_budget_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取超支提醒"""
    alerts = []
    
    # 获取所有激活的预算
    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.is_active == True
    ).all()
    
    for budget in budgets:
        # 计算该预算周期内的已花费金额
        filters = [
            Category.user_id == current_user.id,
            Record.type == RecordType.EXPENSE,
            Record.date >= budget.start_date,
        ]
        
        # 如果有结束日期，只计算到结束日期
        if budget.end_date is not None:
            filters.append(Record.date <= budget.end_date)
        
        spent_amount = db.query(Record).join(Category).filter(*filters)
        
        # 如果预算有分类限制，只计算该分类的支出
        if budget.category_id:
            spent_amount = spent_amount.filter(Category.id == budget.category_id)
        
        spent_amount = spent_amount.with_entities(Record.amount).all()
        total_spent = sum([s[0] for s in spent_amount]) if spent_amount else 0.0
        
        remaining = budget.amount - total_spent
        
        # 判断警告类型
        usage_ratio = total_spent / budget.amount if budget.amount > 0 else 0
        
        if usage_ratio >= 1.0:
            alert_type = "over_budget"
        elif usage_ratio >= 0.8:
            alert_type = "warning"
        else:
            continue  # 没有达到警告阈值，跳过
        
        # 获取分类名称
        category_name = None
        if budget.category_id:
            category = db.query(Category).filter(Category.id == budget.category_id).first()
            if category:
                category_name = category.name
        
        alert = {
            "budget_id": budget.id,
            "budget_name": budget.name,
            "category_name": category_name,
            "budget_amount": budget.amount,
            "spent_amount": total_spent,
            "remaining_amount": remaining,
            "alert_type": alert_type
        }
        
        alerts.append(alert)
    
    return {"alerts": alerts}


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取预算详情"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预算不存在"
        )
    
    return budget


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新预算"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预算不存在"
        )
    
    # 验证分类存在（如果提供了category_id）
    if budget_data.category_id is not None:
        if budget_data.category_id:
            category = db.query(Category).filter(
                Category.id == budget_data.category_id,
                Category.user_id == current_user.id
            ).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="分类不存在"
                )
        budget.category_id = budget_data.category_id
    
    # 更新字段
    if budget_data.name is not None:
        budget.name = budget_data.name
    
    if budget_data.amount is not None:
        budget.amount = budget_data.amount
    
    if budget_data.period_type is not None:
        budget.period_type = BudgetPeriodType(budget_data.period_type)
    
    if budget_data.start_date is not None:
        budget.start_date = budget_data.start_date
    
    if budget_data.end_date is not None:
        budget.end_date = budget_data.end_date
    
    if budget_data.is_active is not None:
        budget.is_active = budget_data.is_active
    
    db.commit()
    db.refresh(budget)
    
    return budget


@router.delete("/{budget_id}", response_model=dict)
async def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除预算"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预算不存在"
        )
    
    db.delete(budget)
    db.commit()
    
    return {"message": "预算删除成功"}
