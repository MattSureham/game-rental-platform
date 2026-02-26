from fastapi import APIRouter

from . import auth, products, orders, wallet

router = APIRouter(prefix="/api")

router.include_router(auth.router)
router.include_router(products.router)
router.include_router(orders.router)
router.include_router(wallet.router)
