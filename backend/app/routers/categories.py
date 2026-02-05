from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.category import Category, CategoryType, CategoryLevel
from app.models.user import User
from app.auth.jwt import get_current_user
from app.schemas.category import CategoryResponse, CategoryCreate, CategoryUpdate, CategoryListResponse

router = APIRouter(prefix="/categories", tags=["分类管理"])


@router.get("", response_model=CategoryListResponse)
async def get_categories(
    type: Optional[CategoryType] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取一级分类列表"""
    query = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.level == CategoryLevel.PRIMARY,
        Category.is_active == True
    )
    
    if type:
        query = query.filter(Category.type == type)
    
    categories = query.order_by(Category.sort_order.asc(), Category.id.asc()).all()
    return {"categories": categories}


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建一级分类"""
    # 检查分类名称是否重复
    existing = db.query(Category).filter(
        Category.name == category_data.name,
        Category.user_id == current_user.id,
        Category.level == CategoryLevel.PRIMARY,
        Category.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类名称已存在"
        )
    
    # 创建分类
    category = Category(
        name=category_data.name,
        type=category_data.type,
        level=CategoryLevel.PRIMARY,
        icon=category_data.icon,
        color=category_data.color,
        sort_order=0,
        is_system=False,
        user_id=current_user.id
    )
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新分类"""
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
    
    # 更新字段
    if category_data.name:
        # 检查名称是否重复
        existing = db.query(Category).filter(
            Category.name == category_data.name,
            Category.user_id == current_user.id,
            Category.id != category_id,
            Category.is_active == True
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分类名称已存在"
            )
        category.name = category_data.name
    
    if category_data.icon is not None:
        category.icon = category_data.icon
    
    if category_data.color is not None:
        category.color = category_data.color
    
    if category_data.sort_order is not None:
        category.sort_order = category_data.sort_order
    
    db.commit()
    db.refresh(category)
    
    return category


@router.delete("/{category_id}", response_model=dict)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除分类（软删除）"""
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
    
    # 软删除分类
    category.is_active = False
    
    # 同时删除所有子分类
    db.query(Category).filter(
        Category.parent_id == category_id,
        Category.user_id == current_user.id
    ).update({"is_active": False})
    
    db.commit()
    
    return {"message": "分类删除成功"}


@router.get("/items", response_model=CategoryListResponse)
async def get_secondary_categories(
    parent_id: Optional[int] = None,
    type: Optional[CategoryType] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取二级分类（按父分类筛选）"""
    query = db.query(Category).filter(
        Category.user_id == current_user.id,
        Category.level == CategoryLevel.SECONDARY,
        Category.is_active == True
    )
    
    if parent_id:
        # 验证父分类是否存在
        parent = db.query(Category).filter(
            Category.id == parent_id,
            Category.user_id == current_user.id,
            Category.level == CategoryLevel.PRIMARY,
            Category.is_active == True
        ).first()
        
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="父分类不存在"
            )
        
        query = query.filter(Category.parent_id == parent_id)
    
    if type:
        query = query.filter(Category.type == type)
    
    categories = query.order_by(Category.sort_order.asc(), Category.id.asc()).all()
    
    return {"categories": categories}


@router.post("/items", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_secondary_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建二级分类"""
    if not category_data.parent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="创建二级分类必须指定父分类"
        )
    
    # 验证父分类
    parent = db.query(Category).filter(
        Category.id == category_data.parent_id,
        Category.user_id == current_user.id,
        Category.level == CategoryLevel.PRIMARY,
        Category.is_active == True
    ).first()
    
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="父分类不存在"
        )
    
    # 检查分类名称是否在同一父分类下重复
    existing = db.query(Category).filter(
        Category.name == category_data.name,
        Category.parent_id == category_data.parent_id,
        Category.user_id == current_user.id,
        Category.level == CategoryLevel.SECONDARY,
        Category.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="分类名称已存在"
        )
    
    # 创建二级分类
    category = Category(
        name=category_data.name,
        type=category_data.type,
        level=CategoryLevel.SECONDARY,
        parent_id=category_data.parent_id,
        icon=category_data.icon,
        color=category_data.color,
        sort_order=0,
        is_system=False,
        user_id=current_user.id
    )
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category


@router.get("/presets", response_model=CategoryListResponse)
async def get_preset_categories(
    type: Optional[CategoryType] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取系统预设分类"""
    query = db.query(Category).filter(
        Category.is_system == True,
        Category.is_active == True
    )
    
    if type:
        query = query.filter(Category.type == type)
    
    categories = query.order_by(Category.sort_order.asc(), Category.id.asc()).all()
    
    return {"categories": categories}
