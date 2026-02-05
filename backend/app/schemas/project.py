from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    budget: Optional[float] = None
    status: str  # active/completed/archived
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[float] = None
    status: Optional[str] = None  # active/completed/archived
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]

    class Config:
        from_attributes = True


class ProjectStats(BaseModel):
    total_budget: Optional[float] = None
    total_expenses: float
    total_income: float
    balance: float

    class Config:
        from_attributes = True
