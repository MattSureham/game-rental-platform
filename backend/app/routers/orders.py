import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..database import get_db
from ..models import User, Product, Order, WalletLog
from ..schemas import (
    OrderCreate, OrderResponse, OrderDetailResponse, OrderContactResponse,
    OrderReturnRequest, OrderDisputeRequest, OrderConfirmRequest,
    MessageResponse
)
from ..routers.auth import get_current_user
from ..config import COMMISSION_RATE, VERIFY_DEADLINE_HOURS

router = APIRouter(prefix="/orders", tags=["订单"])


def generate_order_no() -> str:
    """生成订单号"""
    return f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"


@router.post("", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建订单"""
    # 获取商品信息
    product = db.query(Product).filter(Product.id == order_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    if product.status != "available":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="商品当前不可租用"
        )

    if product.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能租用自己的商品"
        )

    # 计算租金
    if order_data.rental_type == "hourly":
        rent_amount = product.hourly_price * order_data.rental_hours
    elif order_data.rental_type == "daily":
        if not product.daily_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该商品不支持按日租赁"
            )
        rent_amount = product.daily_price * (order_data.rental_hours / 24)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的租赁类型"
        )

    # 计算佣金
    commission_fee = rent_amount * COMMISSION_RATE
    total_amount = rent_amount + product.deposit

    # 创建订单
    order = Order(
        order_no=generate_order_no(),
        renter_id=current_user.id,
        lender_id=product.owner_id,
        product_id=product.id,
        rental_type=order_data.rental_type,
        rental_hours=order_data.rental_hours,
        rent_amount=rent_amount,
        deposit_amount=product.deposit,
        commission_rate=COMMISSION_RATE,
        commission_fee=commission_fee,
        total_amount=total_amount,
        status="PENDING_PAYMENT"
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return OrderResponse.model_validate(order)


@router.get("", response_model=List[OrderResponse])
def get_orders(
    status: Optional[str] = None,
    role: Optional[str] = None,  # renter/lender
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取订单列表"""
    query = db.query(Order)

    if role == "renter":
        query = query.filter(Order.renter_id == current_user.id)
    elif role == "lender":
        query = query.filter(Order.lender_id == current_user.id)
    else:
        # 返回用户参与的所有订单
        query = query.filter(
            (Order.renter_id == current_user.id) | (Order.lender_id == current_user.id)
        )

    if status:
        query = query.filter(Order.status == status)

    orders = query.order_by(Order.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return [OrderResponse.model_validate(o) for o in orders]


@router.get("/renting", response_model=List[OrderResponse])
def get_renting_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取正在租用的订单 (作为租客)"""
    orders = db.query(Order) \
        .filter(Order.renter_id == current_user.id) \
        .filter(Order.status == "PAID") \
        .order_by(Order.created_at.desc()) \
        .all()
    return [OrderResponse.model_validate(o) for o in orders]


@router.get("/lending", response_model=List[OrderResponse])
def get_lending_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取正在出租的订单 (作为房东)"""
    orders = db.query(Order) \
        .filter(Order.lender_id == current_user.id) \
        .filter(Order.status.in_(["PAID", "RETURNED"])) \
        .order_by(Order.created_at.desc()) \
        .all()
    return [OrderResponse.model_validate(o) for o in orders]


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取订单详情"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    # 检查权限：只有订单双方可以查看
    if order.renter_id != current_user.id and order.lender_id != current_user.id:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限查看此订单"
            )

    return OrderDetailResponse.model_validate(order)


@router.get("/{order_id}/contact", response_model=OrderContactResponse)
def get_order_contact(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取订单联系方式 (隐私保护：支付后才可见)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    # 检查权限：只有订单双方可以查看
    if order.renter_id != current_user.id and order.lender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看此订单"
        )

    # 检查订单状态：必须已支付才能查看联系方式
    if order.status not in ["PAID", "RETURNED", "COMPLETED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="支付后方可查看联系方式"
        )

    # 获取对方信息
    if current_user.id == order.renter_id:
        contact_user = db.query(User).filter(User.id == order.lender_id).first()
    else:
        contact_user = db.query(User).filter(User.id == order.renter_id).first()

    if not contact_user or not contact_user.wechat_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对方未设置微信号"
        )

    return OrderContactResponse(wechat_id=contact_user.wechat_id)


@router.post("/{order_id}/pay", response_model=OrderResponse)
def pay_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """支付订单 (模拟支付)"""

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if order.renter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作此订单"
        )

    if order.status != "PENDING_PAYMENT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单状态不正确"
        )

    # 检查余额 - 使用 float 避免 Decimal 比较问题
    if float(current_user.balance) < float(order.total_amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="余额不足，请先充值"
        )

    # 记录支付前余额
    balance_before_payment = float(current_user.balance)

    # 扣除余额 (资金托管)
    current_user.balance = float(current_user.balance) - float(order.total_amount)

    # 更新商品状态
    product = db.query(Product).filter(Product.id == order.product_id).first()
    product.status = "rented"

    # 更新订单状态
    now = datetime.utcnow()
    order.status = "PAID"
    order.start_time = now
    order.end_time = now + timedelta(hours=order.rental_hours)

    # 记录资金流水 - 使用正确的余额
    log = WalletLog(
        user_id=current_user.id,
        order_id=order.id,
        amount=order.total_amount,
        type="PAYMENT",
        direction="expense",
        balance_before=balance_before_payment,
        balance_after=float(current_user.balance),
        description=f"支付订单 {order.order_no}"
    )
    db.add(log)

    db.commit()
    db.refresh(order)

    return OrderResponse.model_validate(order)


@router.post("/{order_id}/return", response_model=OrderResponse)
def return_order(
    order_id: int,
    request: OrderReturnRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """确认归还"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if order.renter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作此订单"
        )

    if order.status != "PAID":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单状态不正确"
        )

    # 更新订单状态
    now = datetime.utcnow()
    order.status = "RETURNED"
    order.return_time = now
    order.verify_deadline = now + timedelta(hours=VERIFY_DEADLINE_HOURS)
    if request.remark:
        order.remark = request.remark

    # 更新商品状态
    product = db.query(Product).filter(Product.id == order.product_id).first()
    product.status = "available"

    db.commit()
    db.refresh(order)

    return OrderResponse.model_validate(order)


@router.post("/{order_id}/confirm", response_model=OrderResponse)
def confirm_order(
    order_id: int,
    request: OrderConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lender 确认验号 (核心结算逻辑)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if order.lender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作此订单"
        )

    if order.status != "RETURNED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单状态不正确"
        )

    # 执行结算
    renter = db.query(User).filter(User.id == order.renter_id).first()
    lender = db.query(User).filter(User.id == order.lender_id).first()

    # 计算Lender收益
    lender_income = float(order.rent_amount) - float(order.commission_fee)

    # 记录操作前的余额
    lender_balance_before = float(lender.balance)
    renter_balance_before = float(renter.balance)

    # Lender获得租金收入
    lender.balance = float(lender.balance) + lender_income

    # Renter获得押金退还
    renter.balance = float(renter.balance) + float(order.deposit_amount)

    # 记录Lender资金流水 (租金收入)
    log_lender = WalletLog(
        user_id=lender.id,
        order_id=order.id,
        amount=lender_income,
        type="RENTAL_INCOME",
        direction="income",
        balance_before=lender_balance_before,
        balance_after=float(lender.balance),
        description=f"订单 {order.order_no} 租金收入"
    )
    db.add(log_lender)

    # 记录Renter押金退还流水
    log_refund = WalletLog(
        user_id=renter.id,
        order_id=order.id,
        amount=order.deposit_amount,
        type="DEPOSIT_REFUND",
        direction="income",
        balance_before=renter_balance_before,
        balance_after=float(renter.balance),
        description=f"订单 {order.order_no} 押金退还"
    )
    db.add(log_refund)

    # 更新订单状态
    order.status = "COMPLETED"
    order.lender_confirm_time = datetime.utcnow()

    db.commit()
    db.refresh(order)

    return OrderResponse.model_validate(order)


@router.post("/{order_id}/dispute", response_model=OrderResponse)
def dispute_order(
    order_id: int,
    request: OrderDisputeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发起维权"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if order.lender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有出租者可以发起维权"
        )

    if order.status != "RETURNED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单状态不正确"
        )

    # 更新订单状态为纠纷中
    order.status = "DISPUTE"
    order.remark = f"维权原因:{request.reason}"

    if request.evidence:
        order.remark += f"\n证据: {request.evidence}"

    db.commit()
    db.refresh(order)

    return OrderResponse.model_validate(order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消订单 (仅限未支付)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    if order.renter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限操作此订单"
        )

    if order.status != "PENDING_PAYMENT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能取消待支付的订单"
        )

    order.status = "CANCELLED"
    db.commit()
    db.refresh(order)

    return OrderResponse.model_validate(order)
