from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.record import Record, RecordType
from app.models.category import Category
from app.models.project import Project
from app.auth.jwt import get_current_user

router = APIRouter(prefix="/statistics", tags=["统计分析"])


class MonthlyStatisticsResponse(BaseModel):
    year: int
    month: int
    total_income: float
    total_expense: float
    balance: float


class RangeStatisticsResponse(BaseModel):
    date_from: str
    date_to: str
    total_income: float
    total_expense: float
    balance: float


class CategoryStatisticsResponse(BaseModel):
    category_id: Optional[int]
    category_name: str
    amount: float
    percentage: float


class ProjectStatisticsResponse(BaseModel):
    project_id: Optional[int]
    project_name: str
    total_income: float
    total_expense: float
    balance: float


class OverviewResponse(BaseModel):
    total_income: float
    total_expense: float
    balance: float
    top_categories: List[CategoryStatisticsResponse]
    top_projects: List[ProjectStatisticsResponse]


@router.get("/monthly", response_model=MonthlyStatisticsResponse)
async def get_monthly_statistics(
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取月度统计"""
    # 验证月份范围
    if month < 1 or month > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="月份必须在1-12之间"
        )
    
    # 计算月份的开始和结束日期
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    
    date_from = datetime(year, month, 1)
    date_to = next_month - timedelta(seconds=1)
    
    # 查询收入
    income_result = db.query(func.sum(Record.amount)).filter(
        Record.user_id == current_user.id,
        Record.type == RecordType.INCOME,
        Record.date >= date_from,
        Record.date <= date_to
    ).scalar()
    total_income = income_result or 0.0
    
    # 查询支出
    expense_result = db.query(func.sum(Record.amount)).filter(
        Record.user_id == current_user.id,
        Record.type == RecordType.EXPENSE,
        Record.date >= date_from,
        Record.date <= date_to
    ).scalar()
    total_expense = expense_result or 0.0
    
    return {
        "year": year,
        "month": month,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "balance": round(total_income - total_expense, 2)
    }


@router.get("/range", response_model=RangeStatisticsResponse)
async def get_range_statistics(
    date_from: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    date_to: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取自定义时间段统计"""
    try:
        date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
        date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="日期格式必须是 YYYY-MM-DD"
        )
    
    # 查询收入
    income_result = db.query(func.sum(Record.amount)).filter(
        Record.user_id == current_user.id,
        Record.type == RecordType.INCOME,
        Record.date >= date_from_dt,
        Record.date <= date_to_dt
    ).scalar()
    total_income = income_result or 0.0
    
    # 查询支出
    expense_result = db.query(func.sum(Record.amount)).filter(
        Record.user_id == current_user.id,
        Record.type == RecordType.EXPENSE,
        Record.date >= date_from_dt,
        Record.date <= date_to_dt
    ).scalar()
    total_expense = expense_result or 0.0
    
    return {
        "date_from": date_from,
        "date_to": date_to,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "balance": round(total_income - total_expense, 2)
    }


@router.get("/categories", response_model=List[CategoryStatisticsResponse])
async def get_category_statistics(
    date_from: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    date_to: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    type: str = Query(..., description="类型: income 或 expense"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取分类占比统计"""
    try:
        date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
        date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="日期格式必须是 YYYY-MM-DD"
        )
    
    # 验证类型
    record_type = None
    if type == "income":
        record_type = RecordType.INCOME
    elif type == "expense":
        record_type = RecordType.EXPENSE
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="类型必须是 income 或 expense"
        )
    
    # 按分类查询金额
    results = db.query(
        Category.id.label("category_id"),
        Category.name.label("category_name"),
        func.sum(Record.amount).label("amount")
    ).outerjoin(Record, Category.id == Record.category_id).filter(
        Record.user_id == current_user.id,
        Record.type == record_type,
        Record.date >= date_from_dt,
        Record.date <= date_to_dt
    ).group_by(Category.id, Category.name).all()
    
    # 计算总金额和百分比
    total_amount = sum(r.amount or 0 for r in results)
    
    category_stats = []
    for r in results:
        amount = r.amount or 0
        percentage = (amount / total_amount * 100) if total_amount > 0 else 0
        category_stats.append({
            "category_id": r.category_id,
            "category_name": r.category_name or "未分类",
            "amount": round(amount, 2),
            "percentage": round(percentage, 2)
        })
    
    # 按金额降序排序
    category_stats.sort(key=lambda x: x["amount"], reverse=True)
    
    return category_stats


@router.get("/projects", response_model=List[ProjectStatisticsResponse])
async def get_project_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目统计"""
    # 获取所有项目（包括用户创建的和关联的）
    projects = db.query(Project).filter(
        (Project.owner_id == current_user.id) |
        (Project.created_by_id == current_user.id)
    ).all()
    
    project_stats = []
    for project in projects:
        # 查询项目的收入
        income_result = db.query(func.sum(Record.amount)).filter(
            Record.project_id == project.id,
            Record.type == RecordType.INCOME
        ).scalar()
        
        # 查询项目的支出
        expense_result = db.query(func.sum(Record.amount)).filter(
            Record.project_id == project.id,
            Record.type == RecordType.EXPENSE
        ).scalar()
        
        total_income = income_result or 0.0
        total_expense = expense_result or 0.0
        
        project_stats.append({
            "project_id": project.id,
            "project_name": project.name,
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "balance": round(total_income - total_expense, 2)
        })
    
    # 按项目名称排序
    project_stats.sort(key=lambda x: x["project_name"])
    
    return project_stats


@router.get("/overview", response_model=OverviewResponse)
async def get_overview_statistics(
    date_from: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取综合概览"""
    # 如果没有提供日期范围，默认当月
    if not date_from or not date_to:
        now = datetime.now()
        date_from_dt = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
        date_to_dt = next_month - timedelta(seconds=1)
        date_from_str = date_from_dt.strftime("%Y-%m-%d")
        date_to_str = date_to_dt.strftime("%Y-%m-%d")
    else:
        try:
            date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
            date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")
            date_from_str = date_from
            date_to_str = date_to
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="日期格式必须是 YYYY-MM-DD"
            )
    
    # 查询总收入和支出
    income_result = db.query(func.sum(Record.amount)).filter(
        Record.user_id == current_user.id,
        Record.type == RecordType.INCOME,
        Record.date >= date_from_dt,
        Record.date <= date_to_dt
    ).scalar()
    
    expense_result = db.query(func.sum(Record.amount)).filter(
        Record.user_id == current_user.id,
        Record.type == RecordType.EXPENSE,
        Record.date >= date_from_dt,
        Record.date <= date_to_dt
    ).scalar()
    
    total_income = income_result or 0.0
    total_expense = expense_result or 0.0
    balance = total_income - total_expense
    
    # 获取 Top 分类（按支出排序）
    category_results = db.query(
        Category.id.label("category_id"),
        Category.name.label("category_name"),
        func.sum(Record.amount).label("amount")
    ).outerjoin(Record, Category.id == Record.category_id).filter(
        Record.user_id == current_user.id,
        Record.type == RecordType.EXPENSE,
        Record.date >= date_from_dt,
        Record.date <= date_to_dt
    ).group_by(Category.id, Category.name).order_by(
        func.sum(Record.amount).desc()
    ).limit(5).all()
    
    top_categories = []
    for r in category_results:
        top_categories.append({
            "category_id": r.category_id,
            "category_name": r.category_name or "未分类",
            "amount": round(r.amount or 0, 2),
            "percentage": 0  # 概览中不需要百分比
        })
    
    # 获取 Top 项目
    project_results = db.query(Project).filter(
        (Project.owner_id == current_user.id) |
        (Project.created_by_id == current_user.id)
    ).all()
    
    top_projects = []
    for project in project_results:
        # 查询项目的支出
        expense_result = db.query(func.sum(Record.amount)).filter(
            Record.project_id == project.id,
            Record.type == RecordType.EXPENSE,
            Record.date >= date_from_dt,
            Record.date <= date_to_dt
        ).scalar()
        
        if expense_result and expense_result > 0:
            top_projects.append({
                "project_id": project.id,
                "project_name": project.name,
                "total_income": 0,
                "total_expense": round(expense_result, 2),
                "balance": round(-expense_result, 2)
            })
    
    # 按支出排序
    top_projects.sort(key=lambda x: x["total_expense"], reverse=True)
    top_projects = top_projects[:5]
    
    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "balance": round(balance, 2),
        "top_categories": top_categories,
        "top_projects": top_projects
    }
