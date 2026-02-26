from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .database import init_db
from .routers import router
from .models import Order, User, WalletLog


# 定时任务: 自动确认订单
async def auto_confirm_orders(app: FastAPI):
    """检查并自动确认到期的订单"""
    from .database import SessionLocal
    
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        
        # 查找所有待验号且已到期的订单
        orders = db.query(Order).filter(
            Order.status == "RETURNED",
            Order.verify_deadline <= now
        ).all()
        
        for order in orders:
            # 自动执行结算逻辑
            renter = db.query(User).filter(User.id == order.renter_id).first()
            lender = db.query(User).filter(User.id == order.lender_id).first()
            
            if renter and lender:
                # 计算Lender收益
                lender_income = float(order.rent_amount) - float(order.commission_fee)
                
                # Lender获得租金收入
                lender.balance = float(lender.balance) + lender_income
                
                # Renter获得押金退还
                renter.balance = float(renter.balance) + float(order.deposit_amount)
                
                # 记录资金流水
                log_lender = WalletLog(
                    user_id=lender.id,
                    order_id=order.id,
                    amount=lender_income,
                    type="RENTAL_INCOME",
                    direction="income",
                    balance_before=float(lender.balance) - lender_income,
                    balance_after=float(lender.balance),
                    description=f"订单 {order.order_no} 租金收入(自动确认)"
                )
                db.add(log_lender)
                
                log_refund = WalletLog(
                    user_id=renter.id,
                    order_id=order.id,
                    amount=order.deposit_amount,
                    type="DEPOSIT_REFUND",
                    direction="income",
                    balance_before=float(renter.balance) - float(order.deposit_amount),
                    balance_after=float(renter.balance),
                    description=f"订单 {order.order_no} 押金退还(自动确认)"
                )
                db.add(log_refund)
                
                # 更新订单状态
                order.status = "COMPLETED"
                order.lender_confirm_time = now
        
        db.commit()
        print(f"[Scheduler] Auto-confirmed {len(orders)} orders")
        
    except Exception as e:
        print(f"[Scheduler] Error: {e}")
        db.rollback()
    finally:
        db.close()


# 创建调度器
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    init_db()
    print("Database initialized")
    
    # 启动定时任务 (每分钟检查一次)
    scheduler.add_job(
        auto_confirm_orders,
        trigger=IntervalTrigger(minutes=1),
        id="auto_confirm",
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started")
    
    yield
    
    # 关闭时停止调度器
    scheduler.shutdown()
    print("Scheduler shutdown")


# 创建FastAPI应用
app = FastAPI(
    title="GameLease API",
    description="游戏账号租赁平台后端API",
    version="1.0.0",
    lifespan=lifespan
)

# 包含路由
app.include_router(router)


@app.get("/")
def root():
    return {"message": "GameLease API Server", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    from .config import HOST, PORT
    
    uvicorn.run(app, host=HOST, port=PORT)
