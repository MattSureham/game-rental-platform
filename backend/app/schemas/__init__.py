from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============ User Schemas ============

class UserBase(BaseModel):
    """用户基础Schema"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """用户创建Schema"""
    openid: str


class UserUpdate(UserBase):
    """用户更新Schema"""
    wechat_id: Optional[str] = None
    role: Optional[str] = None


class UserResponse(UserBase):
    """用户响应Schema"""
    id: int
    openid: Optional[str] = None
    wechat_id: Optional[str] = None
    balance: Decimal
    frozen_balance: Decimal
    credit_score: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class WechatIdUpdate(BaseModel):
    """微信号更新Schema"""
    wechat_id: str = Field(..., min_length=6, max_length=64)


# ============ Product Schemas ============

class ProductImage(BaseModel):
    """商品图片Schema"""
    url: str


class ProductBase(BaseModel):
    """商品基础Schema"""
    game_category: str = Field(..., max_length=32)
    game_name: str = Field(..., max_length=64)
    title: str = Field(..., max_length=128)
    description: Optional[str] = None
    images: List[str] = []
    hourly_price: Decimal = Field(..., gt=0)
    daily_price: Optional[Decimal] = None
    deposit: Decimal = Field(..., ge=0)


class ProductCreate(ProductBase):
    """商品创建Schema"""
    pass


class ProductUpdate(BaseModel):
    """商品更新Schema"""
    game_category: Optional[str] = None
    game_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = None
    hourly_price: Optional[Decimal] = None
    daily_price: Optional[Decimal] = None
    deposit: Optional[Decimal] = None
    status: Optional[str] = None


class ProductResponse(ProductBase):
    """商品响应Schema"""
    id: int
    owner_id: int
    status: str
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """商品列表响应Schema"""
    id: int
    game_category: str
    game_name: str
    title: str
    images: List[str]
    hourly_price: Decimal
    deposit: Decimal
    status: str
    view_count: int

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    """分类响应Schema"""
    id: int
    name: str
    icon: Optional[str] = None


# ============ Order Schemas ============

class OrderCreate(BaseModel):
    """订单创建Schema"""
    product_id: int
    rental_type: str = "hourly"
    rental_hours: int = Field(..., gt=0, le=720)  # 最多30天


class OrderResponse(BaseModel):
    """订单响应Schema"""
    id: int
    order_no: str
    renter_id: int
    lender_id: int
    product_id: int
    rental_type: str
    rental_hours: int
    rent_amount: Decimal
    deposit_amount: Decimal
    commission_rate: Decimal
    commission_fee: Decimal
    total_amount: Decimal
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    return_time: Optional[datetime]
    verify_deadline: Optional[datetime]
    lender_confirm_time: Optional[datetime]
    remark: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class OrderDetailResponse(OrderResponse):
    """订单详情响应Schema (包含敏感信息)"""
    account_info: Optional[str] = None

    class Config:
        from_attributes = True


class OrderContactResponse(BaseModel):
    """订单联系方式响应Schema"""
    wechat_id: str


class OrderReturnRequest(BaseModel):
    """订单归还请求Schema"""
    remark: Optional[str] = None


class OrderDisputeRequest(BaseModel):
    """订单维权请求Schema"""
    reason: str = Field(..., min_length=10)
    evidence: Optional[str] = None


class OrderConfirmRequest(BaseModel):
    """订单确认请求Schema"""
    remark: Optional[str] = None


# ============ Wallet Schemas ============

class WalletBalanceResponse(BaseModel):
    """钱包余额响应Schema"""
    balance: Decimal
    frozen_balance: Decimal
    total: Decimal

    class Config:
        from_attributes = True


class WalletLogResponse(BaseModel):
    """资金流水响应Schema"""
    id: int
    order_id: Optional[int]
    amount: Decimal
    type: str
    direction: str
    balance_before: Decimal
    balance_after: Decimal
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RechargeRequest(BaseModel):
    """充值请求Schema"""
    amount: Decimal = Field(..., gt=0)


class WithdrawRequest(BaseModel):
    """提现请求Schema"""
    amount: Decimal = Field(..., gt=0)


# ============ Auth Schemas ============

class LoginRequest(BaseModel):
    """微信登录请求Schema"""
    code: str


class LoginResponse(BaseModel):
    """登录响应Schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============ Common Schemas ============

class MessageResponse(BaseModel):
    """通用消息响应Schema"""
    message: str


class ErrorResponse(BaseModel):
    """错误响应Schema"""
    detail: str
