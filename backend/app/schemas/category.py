from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.category import CategoryType


class CategoryResponse(BaseModel):
    id: int
    name: str
    type: CategoryType
    level: int  # 1=一级, 2=二级
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: int
    is_system: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str
    type: CategoryType
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None

    class Config:
        from_attributes = True


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    categories: list[CategoryResponse]

    class Config:
        from_attributes = True
