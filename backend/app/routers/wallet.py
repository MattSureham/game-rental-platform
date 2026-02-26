from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, WalletLog
from ..schemas import (
    WalletBalanceResponse, WalletLogResponse, 
    RechargeRequest, WithdrawRequest, MessageResponse
)
from ..routers.auth import get_current_user

router = APIRouter(prefix="/wallet", tags=["钱包"])


@router.get("/balance", response_model=WalletBalanceResponse)
def get_balance(
    current_user: User = Depends(get_current_user)
):
    """获取钱包余额"""
    balance = float(current_user.balance) if current_user.balance else 0
    frozen = float(current_user.frozen_balance) if current_user.frozen_balance else 0
    
    return WalletBalanceResponse(
        balance=balance,
        frozen_balance=frozen,
        total=balance + frozen
    )


@router.get("/logs", response_model=List[WalletLogResponse])
def get_wallet_logs(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取资金流水"""
    logs = db.query(WalletLog) \
        .filter(WalletLog.user_id == current_user.id) \
        .order_by(WalletLog.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    return [WalletLogResponse.model_validate(log) for log in logs]


@router.post("/recharge", response_model=WalletBalanceResponse)
def recharge(
    request: RechargeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    充值 (模拟)
    实际项目中需要调用微信支付API
    """
    amount = float(request.amount)
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="充值金额必须大于0"
        )

    # 记录充值前余额
    balance_before = float(current_user.balance) if current_user.balance else 0
    
    # 增加余额
    current_user.balance = (balance_before + amount)

    # 记录流水
    log = WalletLog(
        user_id=current_user.id,
        amount=amount,
        type="RECHARGE",
        direction="income",
        balance_before=balance_before,
        balance_after=balance_before + amount,
        description=f"充值 {amount} 元"
    )
    db.add(log)
    db.commit()

    return WalletBalanceResponse(
        balance=balance_before + amount,
        frozen_balance=float(current_user.frozen_balance) if current_user.frozen_balance else 0,
        total=balance_before + amount + (float(current_user.frozen_balance) if current_user.frozen_balance else 0)
    )


@router.post("/withdraw", response_model=WalletBalanceResponse)
def withdraw(
    request: WithdrawRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提现 (模拟)
    实际项目中需要审核和打款
    """
    amount = float(request.amount)
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="提现金额必须大于0"
        )

    available_balance = float(current_user.balance) if current_user.balance else 0
    
    if available_balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="余额不足"
        )

    # 记录提现前余额
    balance_before = available_balance
    
    # 扣除余额
    current_user.balance = available_balance - amount

    # 记录流水
    log = WalletLog(
        user_id=current_user.id,
        amount=amount,
        type="WITHDRAWAL",
        direction="expense",
        balance_before=balance_before,
        balance_after=balance_before - amount,
        description=f"提现 {amount} 元"
    )
    db.add(log)
    db.commit()

    return WalletBalanceResponse(
        balance=balance_before - amount,
        frozen_balance=float(current_user.frozen_balance) if current_user.frozen_balance else 0,
        total=balance_before - amount
    )
