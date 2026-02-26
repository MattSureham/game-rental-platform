from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(128), unique=True, index=True, nullable=True)  # 微信openid
    nickname = Column(String(64), nullable=True)
    avatar_url = Column(String(256), nullable=True)
    phone = Column(String(20), nullable=True)
    wechat_id = Column(String(64), nullable=True)  # 微信号 (加密存储)
    balance = Column(Numeric(10, 2), default=0)  # 钱包余额
    frozen_balance = Column(Numeric(10, 2), default=0)  # 冻结金额 (押金)
    credit_score = Column(Integer, default=100)  # 信誉分
    role = Column(String(16), default="renter")  # 角色: renter/lender/admin
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    products = relationship("Product", back_populates="owner", lazy="dynamic")
    orders_as_renter = relationship("Order", foreign_keys="Order.renter_id", back_populates="renter")
    orders_as_lender = relationship("Order", foreign_keys="Order.lender_id", back_populates="lender")
    wallet_logs = relationship("WalletLog", back_populates="user", lazy="dynamic")


class Product(Base):
    """商品/账号模型"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_category = Column(String(32), nullable=False)  # 游戏分类
    game_name = Column(String(64), nullable=False)  # 游戏名称
    title = Column(String(128), nullable=False)  # 商品标题
    description = Column(Text, nullable=True)  # 详细描述
    images = Column(JSON, default=list)  # 图片URL列表
    hourly_price = Column(Numeric(8, 2), nullable=False)  # 时租金
    daily_price = Column(Numeric(8, 2), nullable=True)  # 日租金
    deposit = Column(Numeric(10, 2), nullable=False)  # 押金金额
    status = Column(String(16), default="available")  # 状态: available/rented/offline
    view_count = Column(Integer, default=0)  # 浏览次数
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    owner = relationship("User", back_populates="products")
    orders = relationship("Order", back_populates="product", lazy="dynamic")


class Order(Base):
    """订单模型"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(32), unique=True, index=True, nullable=False)
    renter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    rental_type = Column(String(16), default="hourly")  # 租赁类型: hourly/daily
    rental_hours = Column(Integer, nullable=False)  # 租赁小时数
    rent_amount = Column(Numeric(10, 2), nullable=False)  # 租金金额
    deposit_amount = Column(Numeric(10, 2), nullable=False)  # 押金金额
    commission_rate = Column(Numeric(5, 2), default=0.10)  # 佣金比例
    commission_fee = Column(Numeric(10, 2), default=0)  # 佣金金额
    total_amount = Column(Numeric(10, 2), nullable=False)  # 总金额
    status = Column(String(32), default="PENDING_PAYMENT")  # 订单状态
    start_time = Column(DateTime, nullable=True)  # 开始时间
    end_time = Column(DateTime, nullable=True)  # 结束时间
    return_time = Column(DateTime, nullable=True)  # 归还时间
    verify_deadline = Column(DateTime, nullable=True)  # 验号截止时间
    lender_confirm_time = Column(DateTime, nullable=True)  # 出租者确认时间
    account_info = Column(Text, nullable=True)  # 账号信息 (加密)
    remark = Column(Text, nullable=True)  # 备注
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    renter = relationship("User", foreign_keys=[renter_id], back_populates="orders_as_renter")
    lender = relationship("User", foreign_keys=[lender_id], back_populates="orders_as_lender")
    product = relationship("Product", back_populates="orders")
    wallet_logs = relationship("WalletLog", back_populates="order")


class WalletLog(Base):
    """资金流水模型"""
    __tablename__ = "wallet_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)  # 金额
    type = Column(String(32), nullable=False)  # 流水类型
    direction = Column(String(8), nullable=False)  # 方向: income/expense
    balance_before = Column(Numeric(10, 2), nullable=False)  # 变动前余额
    balance_after = Column(Numeric(10, 2), nullable=False)  # 变动后余额
    description = Column(String(256), nullable=True)  # 描述
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    user = relationship("User", back_populates="wallet_logs")
    order = relationship("Order", back_populates="wallet_logs")
