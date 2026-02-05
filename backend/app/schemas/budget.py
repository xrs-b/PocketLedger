from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category_id: Optional[int] = None
    name: str
    amount: float
    period_type: str  # monthly/yearly
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BudgetCreate(BaseModel):
    category_id: Optional[int] = None
    name: str
    amount: float
    period_type: str  # monthly/yearly
    start_date: datetime
    end_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class BudgetUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    amount: Optional[float] = None
    period_type: Optional[str] = None  # monthly/yearly
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class BudgetListResponse(BaseModel):
    budgets: list[BudgetResponse]

    class Config:
        from_attributes = True


class BudgetAlert(BaseModel):
    budget_id: int
    budget_name: str
    category_name: Optional[str] = None
    budget_amount: float
    spent_amount: float
    remaining_amount: float
    alert_type: str  # warning/over_budget

    class Config:
        from_attributes = True
