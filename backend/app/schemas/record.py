from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.record import RecordType


class RecordResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    amount: float
    type: RecordType
    description: Optional[str] = None
    date: datetime
    payer_count: int
    payer_per_share: Optional[float] = None
    is_aa: bool
    project_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RecordCreate(BaseModel):
    category_id: int
    amount: float
    type: RecordType
    description: Optional[str] = None
    date: datetime
    payer_count: int = 1
    is_aa: bool = False
    project_id: Optional[int] = None

    class Config:
        from_attributes = True


class RecordUpdate(BaseModel):
    category_id: Optional[int] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    payer_count: Optional[int] = None
    is_aa: Optional[bool] = None
    project_id: Optional[int] = None

    class Config:
        from_attributes = True


class RecordListResponse(BaseModel):
    records: list[RecordResponse]
    total: int
    page: int
    page_size: int

    class Config:
        from_attributes = True


class CategoryInfo(BaseModel):
    id: int
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None

    class Config:
        from_attributes = True


class RecordWithCategory(RecordResponse):
    category: Optional[CategoryInfo] = None

    class Config:
        from_attributes = True
