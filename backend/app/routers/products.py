from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Product
from ..schemas import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    CategoryResponse, MessageResponse
)
from ..routers.auth import get_current_user

router = APIRouter(prefix="/products", tags=["商品"])

# 游戏分类
GAME_CATEGORIES = [
    {"id": 1, "name": "王者荣耀", "icon": "/static/icons/wzry.png"},
    {"id": 2, "name": "和平精英", "icon": "/static/icons/hpjy.png"},
    {"id": 3, "name": "原神", "icon": "/static/icons/ys.png"},
    {"id": 4, "name": "英雄联盟", "icon": "/static/icons/lol.png"},
    {"id": 5, "name": "崩坏星穹铁道", "icon": "/static/icons/bhxc.png"},
    {"id": 6, "name": "光遇", "icon": "/static/icons/gy.png"},
    {"id": 7, "name": "第五人格", "icon": "/static/icons/dwrg.png"},
    {"id": 8, "name": "其他", "icon": "/static/icons/other.png"},
]


@router.get("/categories", response_model=List[CategoryResponse])
def get_categories():
    """获取游戏分类列表"""
    return GAME_CATEGORIES


@router.get("", response_model=List[ProductListResponse])
def get_products(
    category: Optional[str] = None,
    game_name: Optional[str] = None,
    status: Optional[str] = "available",
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取商品列表"""
    query = db.query(Product)

    if category:
        query = query.filter(Product.game_category == category)
    if game_name:
        query = query.filter(Product.game_name.ilike(f"%{game_name}%"))
    if status:
        query = query.filter(Product.status == status)
    if keyword:
        query = query.filter(Product.title.ilike(f"%{keyword}%"))

    products = query.order_by(Product.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return products


@router.get("/my", response_model=List[ProductListResponse])
def get_my_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的商品列表"""
    products = db.query(Product) \
        .filter(Product.owner_id == current_user.id) \
        .order_by(Product.created_at.desc()) \
        .all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """获取商品详情"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    # 增加浏览次数
    product.view_count += 1
    db.commit()

    return ProductResponse.model_validate(product)


@router.post("", response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发布商品"""
    # 检查用户是否设置了微信号
    if not current_user.wechat_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先设置微信号后再发布商品"
        )

    product = Product(
        owner_id=current_user.id,
        **product_data.model_dump()
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """编辑商品"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限编辑此商品"
        )

    for key, value in product_data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)

    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", response_model=MessageResponse)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除/下架商品"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此商品"
        )

    # 软删除：设置为下架状态
    product.status = "offline"
    product.updated_at = datetime.utcnow()
    db.commit()

    return MessageResponse(message="商品已下架")
